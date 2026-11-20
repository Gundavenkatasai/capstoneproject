"""
CivicMind AI — Background Tasks & Observability Administration API
Endpoints for inspecting Celery broker, worker health, registered queues,
outbox backlog statistics, and triggering manual dispatch / cleanup operations.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
import redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.outbox import OutboxEvent
from app.models.user import User
from app.tasks.grievance import dispatch_outbox_events_task
from app.tasks.maintenance import cleanup_abandoned_evidence_task

router = APIRouter(prefix="/admin/tasks", tags=["Background Processing Infrastructure"])


class TaskHealthResponse(BaseModel):
    broker_status: str
    broker_url: str
    workers_online: int
    worker_names: List[str]
    registered_queues: List[str]
    registered_tasks: List[str]
    outbox_backlog: Dict[str, int]
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OutboxEventResponse(BaseModel):
    id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    status: str
    attempts: int
    max_attempts: int
    correlation_id: Optional[str] = None
    error_details: Optional[str] = None
    scheduled_for: datetime
    processed_at: Optional[datetime] = None
    created_at: datetime


class OutboxListResponse(BaseModel):
    items: List[OutboxEventResponse]
    total: int
    page: int
    limit: int
    pages: int


class OutboxDispatchResponse(BaseModel):
    status: str
    dispatched: int
    failed: int


class EvidenceCleanupRequest(BaseModel):
    retention_hours: Optional[int] = Field(default=None, ge=1, le=8760)


class EvidenceCleanupResponse(BaseModel):
    status: str
    deleted_count: int
    reclaimed_bytes: int
    retention_hours: int
    cutoff: str
    errors: List[str]


@router.get(
    "/health",
    response_model=TaskHealthResponse,
    summary="Background Processing Health & Diagnostics",
    description="Inspect Celery broker connectivity, active worker nodes, registered task queues, and transactional outbox backlog.",
)
async def get_task_processing_health(
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> TaskHealthResponse:
    # 1. Check Redis broker connectivity
    broker_status = "disconnected"
    try:
        r = redis.from_url(settings.redis_connection_url)
        if r.ping():
            broker_status = "connected"
    except Exception:
        broker_status = "disconnected"

    # Mask Redis broker URL for safe administrative display
    masked_broker_url = settings.celery_broker.split("@")[-1] if "@" in settings.celery_broker else settings.celery_broker

    # 2. Inspect active Celery workers (with fast 300ms timeout so API never hangs)
    worker_names: List[str] = []
    try:
        ping_res = celery_app.control.ping(timeout=0.3)
        if ping_res:
            for item in ping_res:
                worker_names.extend(item.keys())
    except Exception:
        worker_names = []

    # 3. Known registered queues
    registered_queues = [q.name for q in celery_app.conf.task_queues]

    # 4. Registered task names
    registered_tasks = [
        "app.tasks.notifications.send_grievance_notification_task",
        "app.tasks.grievance.dispatch_outbox_events_task",
        "app.tasks.grievance.reconcile_stale_outbox_events_task",
        "app.tasks.grievance.process_grievance_lifecycle_event_task",
        "app.tasks.maintenance.cleanup_abandoned_evidence_task",
        "app.tasks.maintenance.periodic_health_check_task",
    ]

    # 5. Outbox backlog statistics
    backlog_counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0, "total": 0}
    try:
        stmt = (
            select(OutboxEvent.status, func.count(OutboxEvent.id))
            .group_by(OutboxEvent.status)
        )
        res = await db.execute(stmt)
        total = 0
        for status_val, count in res.all():
            backlog_counts[status_val] = count
            total += count
        backlog_counts["total"] = total
    except Exception:
        pass

    return TaskHealthResponse(
        broker_status=broker_status,
        broker_url=f"redis://{masked_broker_url}",
        workers_online=len(worker_names),
        worker_names=worker_names,
        registered_queues=registered_queues,
        registered_tasks=registered_tasks,
        outbox_backlog=backlog_counts,
    )


@router.get(
    "/outbox",
    response_model=OutboxListResponse,
    summary="List Transactional Outbox Events",
    description="Paginated inspection of transactional outbox events with status and event-type filtering.",
)
async def list_outbox_events(
    status_filter: Optional[str] = Query(None, alias="status"),
    event_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
) -> OutboxListResponse:
    query = select(OutboxEvent)
    count_query = select(func.count(OutboxEvent.id))

    if status_filter:
        query = query.where(OutboxEvent.status == status_filter)
        count_query = count_query.where(OutboxEvent.status == status_filter)

    if event_type:
        query = query.where(OutboxEvent.event_type == event_type)
        count_query = count_query.where(OutboxEvent.event_type == event_type)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    offset = (page - 1) * limit
    items_stmt = query.order_by(OutboxEvent.created_at.desc()).offset(offset).limit(limit)
    items_res = await db.execute(items_stmt)
    records = items_res.scalars().all()

    items = [
        OutboxEventResponse(
            id=str(r.id),
            event_type=r.event_type,
            aggregate_type=r.aggregate_type,
            aggregate_id=r.aggregate_id,
            status=r.status,
            attempts=r.attempts,
            max_attempts=r.max_attempts,
            correlation_id=r.correlation_id,
            error_details=r.error_details,
            scheduled_for=r.scheduled_for,
            processed_at=r.processed_at,
            created_at=r.created_at,
        )
        for r in records
    ]

    return OutboxListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 1,
    )


@router.post(
    "/outbox/dispatch",
    response_model=OutboxDispatchResponse,
    summary="Trigger Outbox Dispatch",
    description="Manually trigger immediate dispatch of pending transactional outbox events to Celery task queues.",
)
async def trigger_outbox_dispatch(
    batch_size: int = Query(50, ge=1, le=500),
    current_user: User = Depends(require_role(["admin"])),
) -> OutboxDispatchResponse:
    result = dispatch_outbox_events_task(batch_size=batch_size)
    return OutboxDispatchResponse(
        status=result.get("status", "completed"),
        dispatched=result.get("dispatched", 0),
        failed=result.get("failed", 0),
    )


@router.post(
    "/evidence/cleanup",
    response_model=EvidenceCleanupResponse,
    summary="Trigger Evidence Upload Cleanup",
    description="Manually trigger cleanup of unattached abandoned evidence uploads older than the specified retention window.",
)
async def trigger_evidence_cleanup(
    body: Optional[EvidenceCleanupRequest] = None,
    current_user: User = Depends(require_role(["admin"])),
) -> EvidenceCleanupResponse:
    retention_hours = body.retention_hours if body else None
    result = cleanup_abandoned_evidence_task(retention_hours=retention_hours)
    return EvidenceCleanupResponse(
        status=result.get("status", "completed"),
        deleted_count=result.get("deleted_count", 0),
        reclaimed_bytes=result.get("reclaimed_bytes", 0),
        retention_hours=result.get("retention_hours", settings.EVIDENCE_CLEANUP_RETENTION_HOURS),
        cutoff=result.get("cutoff", ""),
        errors=result.get("errors", []),
    )
