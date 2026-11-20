"""
CivicMind AI — Grievance Lifecycle & Outbox Background Tasks
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
import uuid
from sqlalchemy import select, func, and_
from app.core.celery_app import celery_app
from app.core.database import get_sync_db
from app.models.outbox import OutboxEvent
from app.models.grievance import Grievance
from app.models.user import User

logger = logging.getLogger("civicmind.tasks.grievance")


@celery_app.task(
    bind=True,
    name="app.tasks.grievance.dispatch_outbox_events_task",
    queue="grievance_processing",
    max_retries=2,
    default_retry_delay=5,
)
def dispatch_outbox_events_task(self, batch_size: int = 50) -> Dict[str, Any]:
    """
    Scans the PostgreSQL transactional outbox for pending events,
    marks them 'processing', publishes corresponding background jobs,
    and transitions them to 'completed' or 'failed'.
    """
    task_id = self.request.id
    dispatched_count = 0
    failed_count = 0

    with get_sync_db() as session:
        # Fetch up to batch_size pending events ready for dispatch
        stmt = (
            select(OutboxEvent)
            .where(
                and_(
                    OutboxEvent.status == "pending",
                    OutboxEvent.scheduled_for <= func.now(),
                )
            )
            .order_by(OutboxEvent.scheduled_for.asc())
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        events = session.execute(stmt).scalars().all()

        if not events:
            return {"status": "noop", "dispatched": 0, "failed": 0}

        logger.info(
            "[OUTBOX_DISPATCH_BATCH] task_id=%s processing %d pending outbox events",
            task_id,
            len(events),
        )

        for event in events:
            event.status = "processing"
            event.attempts += 1
            session.flush()

            try:
                # Dispatch downstream lifecycle processing
                process_grievance_lifecycle_event_task.delay(
                    event_id=str(event.id),
                    event_type=event.event_type,
                    grievance_id=event.aggregate_id,
                    payload=event.payload,
                    correlation_id=event.correlation_id,
                )
                
                event.status = "completed"
                event.processed_at = datetime.now(timezone.utc)
                event.error_details = None
                dispatched_count += 1
            except Exception as ex:
                logger.error(
                    "[OUTBOX_EVENT_FAILED] event_id=%s error=%s",
                    str(event.id),
                    str(ex),
                )
                event.error_details = str(ex)
                if event.attempts >= event.max_attempts:
                    event.status = "failed"
                else:
                    event.status = "pending"  # Eligible for retry
                failed_count += 1

        session.commit()

    return {
        "status": "completed",
        "dispatched": dispatched_count,
        "failed": failed_count,
    }


@celery_app.task(
    bind=True,
    name="app.tasks.grievance.reconcile_stale_outbox_events_task",
    queue="grievance_processing",
    max_retries=1,
)
def reconcile_stale_outbox_events_task(
    self,
    stale_threshold_seconds: int = 300,
) -> Dict[str, Any]:
    """
    Identifies outbox events stuck in 'processing' status (e.g. due to worker crash)
    and resets them to 'pending' or 'failed'.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=stale_threshold_seconds)
    reconciled_count = 0
    failed_count = 0

    with get_sync_db() as session:
        stmt = (
            select(OutboxEvent)
            .where(
                and_(
                    OutboxEvent.status == "processing",
                    OutboxEvent.updated_at < cutoff,
                )
            )
            .with_for_update(skip_locked=True)
        )
        stale_events = session.execute(stmt).scalars().all()

        for event in stale_events:
            if event.attempts >= event.max_attempts:
                event.status = "failed"
                event.error_details = f"Reconciler: stuck in processing past {cutoff.isoformat()}; exceeded max attempts"
                failed_count += 1
            else:
                event.status = "pending"
                reconciled_count += 1

        session.commit()

    if stale_events:
        logger.warning(
            "[OUTBOX_RECONCILIATION] found %d stale events (reset=%d, failed=%d)",
            len(stale_events),
            reconciled_count,
            failed_count,
        )

    return {
        "status": "reconciled",
        "stale_found": len(stale_events),
        "reset_to_pending": reconciled_count,
        "marked_failed": failed_count,
    }


@celery_app.task(
    bind=True,
    name="app.tasks.grievance.process_grievance_lifecycle_event_task",
    queue="grievance_processing",
    max_retries=3,
    default_retry_delay=5,
)
def process_grievance_lifecycle_event_task(
    self,
    event_id: str,
    event_type: str,
    grievance_id: str,
    payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Processes asynchronous side-effects of grievance lifecycle events,
    such as citizen notification formatting and dispatch.
    """
    from app.tasks.notifications import send_grievance_notification_task

    tracking_id = payload.get("tracking_id", grievance_id)
    title = payload.get("title", "Grievance")
    citizen_email = payload.get("citizen_email")
    citizen_phone = payload.get("citizen_phone")

    # If email/phone not present in payload, query user record
    if not citizen_email:
        with get_sync_db() as session:
            grv = session.get(Grievance, grievance_id)
            if grv and grv.citizen_id:
                user = session.get(User, grv.citizen_id)
                if user:
                    citizen_email = user.email
                    citizen_phone = user.phone_number

    subject = f"CivicMind Update: {tracking_id} - {event_type.replace('grievance.', '').replace('_', ' ').title()}"
    body = (
        f"Dear Citizen,\n\n"
        f"Your grievance '{title}' (Tracking ID: {tracking_id}) has a new update: {event_type}.\n\n"
        f"Details: {payload.get('notes', payload.get('action_summary', 'Status updated successfully'))}\n\n"
        f"Track your grievance status at: http://localhost:3000/track/{tracking_id}\n\n"
        f"Thank you,\nCivicMind Municipal Grievance Administration"
    )

    if citizen_email:
        send_grievance_notification_task.delay(
            event_id=event_id,
            notification_type=event_type,
            recipient_email=citizen_email,
            recipient_phone=citizen_phone,
            subject=subject,
            body=body,
            channel="email",
            metadata={"grievance_id": grievance_id, "tracking_id": tracking_id},
            correlation_id=correlation_id,
        )

    # Trigger ML 768-dim embedding generation & duplicate scan for submitted grievances
    if "submitted" in event_type.lower():
        try:
            from app.tasks.ml import generate_grievance_embedding_task
            generate_grievance_embedding_task.delay(grievance_id=grievance_id)
        except Exception as ex:
            logger.warning("[OUTBOX_ML_EMBEDDING_DISPATCH_WARN] grievance_id=%s error=%s", grievance_id, str(ex))

    return {
        "status": "processed",
        "event_type": event_type,
        "tracking_id": tracking_id,
        "notification_queued": bool(citizen_email),
    }
