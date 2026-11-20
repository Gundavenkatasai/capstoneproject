"""
CivicMind AI — Background Maintenance & Periodic Health Tasks
"""

import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
import redis
from sqlalchemy import select, func, and_, text
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import get_sync_db
from app.models.evidence import GrievanceEvidence
from app.models.outbox import OutboxEvent

logger = logging.getLogger("civicmind.tasks.maintenance")

UPLOAD_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "evidence"


@celery_app.task(
    bind=True,
    name="app.tasks.maintenance.cleanup_abandoned_evidence_task",
    queue="maintenance",
    max_retries=1,
)
def cleanup_abandoned_evidence_task(
    self,
    retention_hours: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Safely purges unattached GrievanceEvidence files uploaded but never associated
    with a completed grievance after the retention threshold.
    
    SAFETY INVARIANT: Never deletes evidence linked to an active grievance
    (grievance_id IS NOT NULL).
    """
    task_id = self.request.id
    hours = retention_hours if retention_hours is not None else settings.EVIDENCE_CLEANUP_RETENTION_HOURS
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    deleted_count = 0
    reclaimed_bytes = 0
    errors = []

    logger.info(
        "[EVIDENCE_CLEANUP_START] task_id=%s retention_hours=%d cutoff=%s",
        task_id,
        hours,
        cutoff.isoformat(),
    )

    with get_sync_db() as session:
        # Strictly select only unattached evidence records older than the cutoff
        stmt = (
            select(GrievanceEvidence)
            .where(
                and_(
                    GrievanceEvidence.grievance_id.is_(None),
                    GrievanceEvidence.created_at < cutoff,
                )
            )
        )
        abandoned_records = session.execute(stmt).scalars().all()

        for evidence in abandoned_records:
            # Secondary runtime safety assertion
            if evidence.grievance_id is not None:
                logger.error(
                    "[CLEANUP_SAFETY_VIOLATION_ABORT] Refusing to delete evidence %s attached to grievance %s",
                    str(evidence.id),
                    evidence.grievance_id,
                )
                continue

            # Safely remove file on disk
            try:
                target_file = (UPLOAD_BASE_DIR / evidence.file_name).resolve()
                if target_file.exists() and target_file.is_file():
                    file_size = target_file.stat().st_size
                    target_file.unlink(missing_ok=True)
                    reclaimed_bytes += file_size
                else:
                    ext = Path(evidence.file_name).suffix.lower()
                    for candidate in UPLOAD_BASE_DIR.glob(f"*{ext}"):
                        if candidate.is_file() and candidate.stat().st_size == evidence.file_size_bytes:
                            file_size = candidate.stat().st_size
                            candidate.unlink(missing_ok=True)
                            reclaimed_bytes += file_size
                            break
            except Exception as ex:
                logger.warning(
                    "[EVIDENCE_FILE_PURGE_ERROR] Could not delete disk file for evidence %s: %s",
                    str(evidence.id),
                    ex,
                )
                errors.append(f"Disk file error on {evidence.id}: {str(ex)}")

            # Remove database record
            session.delete(evidence)
            deleted_count += 1

        session.commit()

    logger.info(
        "[EVIDENCE_CLEANUP_COMPLETE] task_id=%s deleted_count=%d reclaimed_bytes=%d errors=%d",
        task_id,
        deleted_count,
        reclaimed_bytes,
        len(errors),
    )

    return {
        "status": "completed",
        "deleted_count": deleted_count,
        "reclaimed_bytes": reclaimed_bytes,
        "retention_hours": hours,
        "cutoff": cutoff.isoformat(),
        "errors": errors,
    }


@celery_app.task(
    bind=True,
    name="app.tasks.maintenance.periodic_health_check_task",
    queue="maintenance",
    max_retries=1,
)
def periodic_health_check_task(self) -> Dict[str, Any]:
    """
    Executes scheduled diagnostic verification of database, broker, and outbox queue backlog.
    """
    db_healthy = False
    redis_healthy = False
    pending_outbox_count = 0
    checked_at = datetime.now(timezone.utc).isoformat()

    # 1. PostgreSQL Check
    try:
        with get_sync_db() as session:
            result = session.execute(text("SELECT 1;")).scalar()
            db_healthy = (result == 1)
            
            # Count outbox pending backlog
            count_stmt = select(func.count(OutboxEvent.id)).where(OutboxEvent.status == "pending")
            pending_outbox_count = session.execute(count_stmt).scalar() or 0
    except Exception as ex:
        logger.error("[HEALTH_CHECK_DB_FAILURE] %s", ex)

    # 2. Redis Broker Check
    try:
        r = redis.from_url(settings.redis_connection_url)
        redis_healthy = bool(r.ping())
    except Exception as ex:
        logger.error("[HEALTH_CHECK_REDIS_FAILURE] %s", ex)

    overall_healthy = db_healthy and redis_healthy

    logger.info(
        "[SCHEDULED_HEALTH_CHECK] overall=%s db=%s redis=%s pending_outbox=%d",
        overall_healthy,
        db_healthy,
        redis_healthy,
        pending_outbox_count,
    )

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "database": db_healthy,
        "redis": redis_healthy,
        "pending_outbox_count": pending_outbox_count,
        "checked_at": checked_at,
    }
