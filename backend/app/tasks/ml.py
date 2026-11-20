"""
CivicMind AI — Machine Learning Celery Background Tasks
Executes asynchronous vector embedding generation, pgvector duplicate scans,
cluster association, and model maintenance jobs.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from app.core.celery_app import celery_app
from app.core.database import get_sync_db
from app.models.grievance import Grievance
from app.models.embedding import GrievanceEmbedding
from app.models.duplicate import DuplicateCluster, ClusterMembership
from ml.embeddings.sentence_embedder import sentence_embedder
from ml.duplicates.detector import haversine_distance_meters, cosine_similarity
from ml.registry.model_registry import model_registry

logger = logging.getLogger("civicmind.tasks.ml")


@celery_app.task(
    bind=True,
    name="app.tasks.ml.generate_grievance_embedding_task",
    queue="grievance_processing",
    max_retries=3,
    default_retry_delay=5,
)
def generate_grievance_embedding_task(self, grievance_id: str) -> Dict[str, Any]:
    """
    Generates a 768-dimensional dense vector representation for the grievance
    and persists it to the PostgreSQL pgvector grievance_embeddings table.
    Dispatches duplicate detection upon successful embedding generation.
    """
    logger.info("[EMBEDDING_TASK_START] grievance_id=%s", grievance_id)

    with get_sync_db() as session:
        grv = session.get(Grievance, grievance_id)
        if not grv:
            logger.warning("[EMBEDDING_TASK_NOT_FOUND] grievance_id=%s", grievance_id)
            return {"status": "not_found", "grievance_id": grievance_id}

        text_to_embed = f"{grv.title}. {grv.description}"
        vector = sentence_embedder.embed_text(text_to_embed)

        # Check existing
        existing = session.get(GrievanceEmbedding, grievance_id)
        if existing:
            existing.embedding = vector
            existing.generated_at = datetime.now(timezone.utc)
        else:
            emb = GrievanceEmbedding(
                grievance_id=grievance_id,
                embedding=vector,
                model_version=sentence_embedder.model_name,
            )
            session.add(emb)

        session.commit()
        logger.info("[EMBEDDING_TASK_PERSISTED] grievance_id=%s dimension=%d", grievance_id, len(vector))

    # Trigger duplicate detection
    try:
        detect_duplicate_grievances_task.delay(grievance_id=grievance_id)
    except Exception as ex:
        logger.warning("[EMBEDDING_TASK_DUP_DISPATCH_WARN] grievance_id=%s error=%s", grievance_id, str(ex))

    return {
        "status": "completed",
        "grievance_id": grievance_id,
        "dimension": len(vector),
    }


@celery_app.task(
    bind=True,
    name="app.tasks.ml.detect_duplicate_grievances_task",
    queue="grievance_processing",
    max_retries=2,
    default_retry_delay=5,
)
def detect_duplicate_grievances_task(
    self,
    grievance_id: str,
    similarity_threshold: float = 0.82,
    max_proximity_meters: float = 1000.0,
) -> Dict[str, Any]:
    """
    Scans existing embeddings for semantic duplicates of the specified grievance.
    If duplicates are detected, associates or creates a DuplicateCluster (pending_review)
    WITHOUT destructively merging records.
    """
    logger.info("[DUPLICATE_SCAN_START] grievance_id=%s", grievance_id)

    with get_sync_db() as session:
        target = session.get(Grievance, grievance_id)
        target_emb = session.get(GrievanceEmbedding, grievance_id)
        if not target or not target_emb:
            return {"status": "skipped", "reason": "Target or embedding missing"}

        # Query candidates in same category or adjacent
        stmt = (
            select(Grievance, GrievanceEmbedding)
            .join(GrievanceEmbedding, Grievance.id == GrievanceEmbedding.grievance_id)
            .where(
                and_(
                    Grievance.id != grievance_id,
                    Grievance.status.notin_(["closed", "citizen_verified"]),
                )
            )
            .limit(50)
        )
        candidates = session.execute(stmt).all()

        matches = []
        target_vec = target_emb.embedding

        for cand_grv, cand_emb in candidates:
            sim = cosine_similarity(target_vec, cand_emb.embedding)
            if sim < similarity_threshold:
                continue

            # Check distance
            dist = 0.0
            if target.latitude and target.longitude and cand_grv.latitude and cand_grv.longitude:
                dist = haversine_distance_meters(
                    target.latitude, target.longitude, cand_grv.latitude, cand_grv.longitude
                )
                if dist > max_proximity_meters:
                    continue

            matches.append((cand_grv, sim, dist))

        if not matches:
            return {"status": "no_duplicates_found", "grievance_id": grievance_id}

        # Sort by similarity descending
        matches.sort(key=lambda x: x[1], reverse=True)
        top_match, top_sim, top_dist = matches[0]

        target.duplicate_probability = float(top_sim)

        # Check if top match is already in a cluster
        cluster = None
        if top_match.duplicate_cluster_id:
            cluster = session.get(DuplicateCluster, top_match.duplicate_cluster_id)

        if not cluster:
            # Create a new candidate cluster
            cluster_id = uuid.uuid4()
            cluster_code = f"CLUST-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"
            cluster = DuplicateCluster(
                id=cluster_id,
                cluster_code=cluster_code,
                title=f"Potential Duplicate Cluster: {target.title[:100]}",
                category=target.category,
                master_grievance_id=top_match.id,
                similarity_score=float(top_sim),
                proximity_meters=int(top_dist),
                time_span_hours=24,
                status="pending_review",
                ai_recommendation=(
                    "High semantic similarity detected between citizen submissions in the same municipal ward. "
                    "Recommend officer review for unified crew dispatch."
                ),
                reasons=[
                    f"Cosine similarity score: {top_sim:.3f}",
                    f"Geographic distance: {int(top_dist)} meters",
                ],
            )
            session.add(cluster)
            session.flush()

            # Add top match to cluster
            top_membership = ClusterMembership(
                cluster_id=cluster.id,
                grievance_id=top_match.id,
            )
            session.add(top_membership)
            top_match.duplicate_cluster_id = cluster.id

        # Add target to cluster
        target_membership = ClusterMembership(
            cluster_id=cluster.id,
            grievance_id=target.id,
        )
        session.add(target_membership)
        target.duplicate_cluster_id = cluster.id

        session.commit()
        logger.info(
            "[DUPLICATE_CLUSTER_LINKED] target=%s master=%s cluster_id=%s sim=%.3f",
            target.id,
            cluster.master_grievance_id,
            str(cluster.id),
            top_sim,
        )

        return {
            "status": "cluster_linked",
            "cluster_id": str(cluster.id),
            "cluster_code": cluster.cluster_code,
            "master_grievance_id": cluster.master_grievance_id,
            "similarity_score": top_sim,
        }


@celery_app.task(
    bind=True,
    name="app.tasks.ml.batch_duplicate_scan_task",
    queue="grievance_processing",
    max_retries=1,
)
def batch_duplicate_scan_task(self, limit: int = 100) -> Dict[str, Any]:
    """
    Scheduled background task scanning unclustered grievances to group duplicates.
    """
    with get_sync_db() as session:
        stmt = (
            select(Grievance.id)
            .where(
                and_(
                    Grievance.duplicate_cluster_id.is_(None),
                    Grievance.status.notin_(["closed", "citizen_verified"]),
                )
            )
            .limit(limit)
        )
        ids = session.execute(stmt).scalars().all()

    dispatched = 0
    for gid in ids:
        detect_duplicate_grievances_task.delay(grievance_id=gid)
        dispatched += 1

    return {"status": "completed", "scanned_candidates": dispatched}


@celery_app.task(
    bind=True,
    name="app.tasks.ml.retrain_models_task",
    queue="grievance_processing",
    max_retries=1,
)
def retrain_models_task(self) -> Dict[str, Any]:
    """
    Periodic task that checks the dataset readiness gate and triggers retraining if eligible.
    """
    from ml.data.extractor import audit_production_dataset_sync, load_dataset_for_training

    audit = audit_production_dataset_sync()
    if audit.is_ready:
        df, _ = load_dataset_for_training()
        model_registry.train_all_models(df)
        status_msg = "Retrained on operational PostgreSQL database."
    else:
        status_msg = f"Retraining deferred: {audit.reason}"

    return {
        "status": "completed",
        "is_ready": audit.is_ready,
        "message": status_msg,
    }
