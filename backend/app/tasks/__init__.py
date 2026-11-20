"""
CivicMind AI — Celery Tasks Package
Exports all background and scheduled task definitions.
"""

from app.tasks.notifications import send_grievance_notification_task
from app.tasks.grievance import (
    dispatch_outbox_events_task,
    reconcile_stale_outbox_events_task,
    process_grievance_lifecycle_event_task,
)
from app.tasks.maintenance import (
    cleanup_abandoned_evidence_task,
    periodic_health_check_task,
)
from app.tasks.ml import (
    generate_grievance_embedding_task,
    detect_duplicate_grievances_task,
    batch_duplicate_scan_task,
    retrain_models_task,
)

__all__ = [
    "send_grievance_notification_task",
    "dispatch_outbox_events_task",
    "reconcile_stale_outbox_events_task",
    "process_grievance_lifecycle_event_task",
    "cleanup_abandoned_evidence_task",
    "periodic_health_check_task",
    "generate_grievance_embedding_task",
    "detect_duplicate_grievances_task",
    "batch_duplicate_scan_task",
    "retrain_models_task",
]
