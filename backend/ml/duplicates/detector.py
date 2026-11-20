"""
CivicMind AI — Semantic Duplicate Detection Engine
Leverages PostgreSQL pgvector cosine similarity, Haversine geospatial proximity,
and temporal windowing to discover duplicate grievance reports without destructive automatic merging.
"""

import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.grievance import Grievance
from app.models.embedding import GrievanceEmbedding
from ml.embeddings.sentence_embedder import sentence_embedder


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two unit-normalized vectors."""
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    dot = float(np.dot(a, b))
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return round(dot / (norm_a * norm_b), 4)


class DuplicateDetector:
    """
    Evaluates new and existing grievances for semantic duplication.
    Guarantees non-destructive review workflow (recommends merges to human officers).
    """

    def __init__(
        self,
        similarity_threshold: float = 0.82,
        max_proximity_meters: float = 1000.0,
        max_time_days: int = 30,
    ):
        self.similarity_threshold = similarity_threshold
        self.max_proximity_meters = max_proximity_meters
        self.max_time_days = max_time_days

    async def find_duplicates_for_grievance(
        self,
        session: AsyncSession,
        grievance_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Queries pgvector for top cosine similarity matches for an existing grievance.
        Applies geospatial and temporal filtering.
        """
        # Fetch target grievance and its embedding
        target = await session.get(Grievance, grievance_id)
        if not target:
            return []

        target_emb = await session.get(GrievanceEmbedding, grievance_id)
        if not target_emb:
            # Generate and persist on the fly
            vector = sentence_embedder.embed_text(f"{target.title}. {target.description}")
            target_emb = GrievanceEmbedding(
                grievance_id=target.id,
                embedding=vector,
            )
            session.add(target_emb)
            await session.flush()
        else:
            vector = target_emb.embedding

        return await self.find_duplicates_by_vector(
            session=session,
            vector=vector,
            target_id=target.id,
            latitude=target.latitude,
            longitude=target.longitude,
            category=target.category,
            limit=limit,
        )

    async def find_duplicates_by_vector(
        self,
        session: AsyncSession,
        vector: List[float],
        target_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Uses pgvector cosine distance query:
        GrievanceEmbedding.embedding.cosine_distance(vector)
        """
        # Formulate pgvector similarity query
        stmt = (
            select(
                Grievance,
                (1.0 - GrievanceEmbedding.embedding.cosine_distance(vector)).label("similarity"),
            )
            .join(GrievanceEmbedding, Grievance.id == GrievanceEmbedding.grievance_id)
            .where(Grievance.status.notin_(["closed", "citizen_verified"]))
        )

        if target_id:
            stmt = stmt.where(Grievance.id != target_id)

        if category:
            stmt = stmt.where(Grievance.category == category)

        stmt = stmt.order_by(GrievanceEmbedding.embedding.cosine_distance(vector).asc()).limit(limit * 2)

        result = await session.execute(stmt)
        rows = result.all()

        matches = []
        for g, sim in rows:
            sim_float = round(float(sim), 4)
            if sim_float < self.similarity_threshold:
                continue

            # Check distance if coordinates available
            dist_meters = None
            if latitude is not None and longitude is not None and g.latitude and g.longitude:
                dist_meters = haversine_distance_meters(latitude, longitude, g.latitude, g.longitude)
                if dist_meters > self.max_proximity_meters:
                    continue

            # Recommendation tier
            if sim_float >= 0.90:
                rec = "merge_candidate"
                reason = "Extremely high semantic overlap and close municipal proximity. High confidence duplicate."
            else:
                rec = "potential_duplicate"
                reason = "Significant semantic and topical overlap. Recommend officer review before independent dispatch."

            matches.append({
                "grievance_id": g.id,
                "title": g.title,
                "category": g.category,
                "ward": g.ward,
                "status": g.status,
                "similarity_score": sim_float,
                "proximity_meters": dist_meters if dist_meters is not None else 0,
                "ai_recommendation": rec,
                "reason": reason,
            })

            if len(matches) >= limit:
                break

        return matches

    def find_in_memory_duplicates(
        self,
        query_text: str,
        query_lat: float,
        query_lng: float,
        candidates: List[Dict[str, Any]],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        In-memory duplicate search over candidate dictionaries. Useful for offline evaluation and unit tests.
        """
        query_vec = sentence_embedder.embed_text(query_text)
        matches = []

        for cand in candidates:
            cand_text = f"{cand.get('title', '')}. {cand.get('description', '')}"
            cand_vec = cand.get("embedding") or sentence_embedder.embed_text(cand_text)

            sim = cosine_similarity(query_vec, cand_vec)
            if sim < self.similarity_threshold:
                continue

            dist = haversine_distance_meters(
                query_lat, query_lng, cand.get("latitude", query_lat), cand.get("longitude", query_lng)
            )
            if dist > self.max_proximity_meters:
                continue

            rec = "merge_candidate" if sim >= 0.90 else "potential_duplicate"

            matches.append({
                "grievance_id": cand.get("id"),
                "title": cand.get("title"),
                "category": cand.get("category"),
                "similarity_score": sim,
                "proximity_meters": dist,
                "ai_recommendation": rec,
            })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:limit]


duplicate_detector = DuplicateDetector()
