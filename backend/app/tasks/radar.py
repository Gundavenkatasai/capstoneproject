"""
CivicMind AI — Geospatial Hotspot & Radar Celery Background Tasks
Phase 6 Geospatial Grievance Intelligence.

Executes periodic and on-demand density-based spatial clustering (DBSCAN)
to discover and update geographic complaint concentrations and risk velocity metrics.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime, timezone

from sqlalchemy import select, and_
from app.core.celery_app import celery_app
from app.core.database import get_sync_db
from app.models.grievance import Grievance
from app.models.hotspot import Hotspot
from ml.geospatial.clustering import SpatialClusterer
from ml.geospatial.radar import EarlyWarningRadar

logger = logging.getLogger("civicmind.tasks.radar")


@celery_app.task(
    bind=True,
    name="app.tasks.radar.scan_geographic_hotspots_task",
    queue="analytics",
    max_retries=2,
    default_retry_delay=10,
)
def scan_geographic_hotspots_task(
    self,
    radius_km: float = 0.5,
    min_samples: int = 2,
) -> Dict[str, Any]:
    """
    Executes DBSCAN clustering over active municipal complaints to synthesize
    or refresh operational early-warning radar hotspots in PostgreSQL.
    Enforces strict segregation against synthetic benchmark records.
    """
    logger.info(
        "[HOTSPOT_SCAN_START] radius_km=%.2f min_samples=%d",
        radius_km,
        min_samples,
    )

    with get_sync_db() as session:
        # Query active grievances with spatial coordinates
        stmt = select(Grievance).where(
            and_(
                Grievance.status.notin_(["resolved", "rejected"]),
                Grievance.latitude.isnot(None),
                Grievance.longitude.isnot(None),
            )
        )
        grievances = session.execute(stmt).scalars().all()

        eligible: List[Dict[str, Any]] = []
        for g in grievances:
            # Exclude synthetic records
            is_synth = (
                str(g.id).startswith("SYN-")
                or (g.metadata_json and g.metadata_json.get("is_synthetic") is True)
            )
            if is_synth:
                continue

            eligible.append({
                "id": g.id,
                "title": g.title,
                "category": g.category,
                "ward": g.ward or "Central Ward",
                "zone": g.zone or "Central Zone",
                "latitude": g.latitude,
                "longitude": g.longitude,
                "priority": g.priority,
                "status": g.status,
                "created_at": g.created_at,
                "is_synthetic": False,
            })

        clusterer = SpatialClusterer(radius_km=radius_km, min_samples=min_samples)
        raw_clusters = clusterer.cluster_grievances(eligible, filter_synthetic=True)

        radar = EarlyWarningRadar()
        hotspots_updated = 0

        for cluster in raw_clusters:
            hotspot_dict = radar.process_cluster_to_hotspot(cluster)

            # Check for existing hotspot in same ward and category
            existing = session.execute(
                select(Hotspot).where(
                    and_(
                        Hotspot.ward == hotspot_dict["ward"],
                        Hotspot.category == hotspot_dict["category"],
                    )
                )
            ).scalar_one_or_none()

            if existing:
                existing.complaint_count = hotspot_dict["complaint_count"]
                existing.risk_score = hotspot_dict["risk_score"]
                existing.risk_level = hotspot_dict["risk_level"]
                existing.trend = hotspot_dict["trend"]
                existing.radius_meters = hotspot_dict["radius_meters"]
                existing.summary = hotspot_dict["summary"]
                existing.historical_velocity = hotspot_dict["historical_velocity"]
            else:
                new_h = Hotspot(
                    id=hotspot_dict["id"],
                    title=hotspot_dict["title"],
                    category=hotspot_dict["category"],
                    zone=hotspot_dict["zone"],
                    ward=hotspot_dict["ward"],
                    latitude=hotspot_dict["latitude"],
                    longitude=hotspot_dict["longitude"],
                    radius_meters=hotspot_dict["radius_meters"],
                    complaint_count=hotspot_dict["complaint_count"],
                    risk_level=hotspot_dict["risk_level"],
                    risk_score=hotspot_dict["risk_score"],
                    trend=hotspot_dict["trend"],
                    summary=hotspot_dict["summary"],
                    recommended_action=hotspot_dict["recommended_action"],
                    historical_velocity=hotspot_dict["historical_velocity"],
                    is_acknowledged=False,
                )
                session.add(new_h)

            hotspots_updated += 1

        session.commit()
        logger.info("[HOTSPOT_SCAN_SUCCESS] updated=%d clusters", hotspots_updated)
        return {
            "status": "success",
            "hotspots_updated": hotspots_updated,
            "eligible_grievances_analyzed": len(eligible),
        }
