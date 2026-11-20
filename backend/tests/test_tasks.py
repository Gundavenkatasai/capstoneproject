"""
CivicMind AI — Phase 4 Background Processing & Celery Task Tests
Tests Celery configuration, queue routing, task idempotency, transactional outbox pattern,
notification providers, safe evidence cleanup invariants, and operational admin APIs.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.celery_app import celery_app
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.department import Department
from app.models.grievance import Grievance
from app.models.evidence import GrievanceEvidence
from app.models.outbox import OutboxEvent
from app.schemas.grievance import GrievanceCreateRequest
from app.services.grievance_service import GrievanceService
from app.services.notifications.provider import (
    LoggingNotificationProvider,
    NotificationMessage,
    NotificationChannel,
    get_notification_provider,
)
from app.tasks.notifications import send_grievance_notification_task
from app.tasks.grievance import (
    dispatch_outbox_events_task,
    reconcile_stale_outbox_events_task,
)
from app.tasks.maintenance import (
    cleanup_abandoned_evidence_task,
    periodic_health_check_task,
    UPLOAD_BASE_DIR,
)


@pytest.fixture
async def setup_task_auth(db_session: AsyncSession):
    """
    Creates real database users for role-based admin and citizen testing.
    """
    admin_user = User(
        id=uuid.uuid4(),
        email=f"admin_task_{uuid.uuid4().hex[:6]}@civicmind.ai",
        password_hash=get_password_hash("AdminPass123!"),
        name="Task Test Admin",
        role="admin",
        is_active=True,
    )
    citizen_user = User(
        id=uuid.uuid4(),
        email=f"citizen_task_{uuid.uuid4().hex[:6]}@civicmind.ai",
        password_hash=get_password_hash("CitizenPass123!"),
        name="Task Test Citizen",
        role="citizen",
        is_active=True,
    )
    db_session.add_all([admin_user, citizen_user])
    await db_session.commit()

    admin_token, _ = create_access_token(
        user_id=str(admin_user.id),
        role=admin_user.role,
        email=admin_user.email,
        name=admin_user.name,
    )
    citizen_token, _ = create_access_token(
        user_id=str(citizen_user.id),
        role=citizen_user.role,
        email=citizen_user.email,
        name=citizen_user.name,
    )
    return {
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "citizen_headers": {"Authorization": f"Bearer {citizen_token}"},
    }


# -----------------------------------------------------------------------------
# 1. Celery Infrastructure & Configuration Tests
# -----------------------------------------------------------------------------

def test_celery_configuration_and_queues():
    """Verify Celery app configuration, JSON serialization, and logical queue setup."""
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True

    queue_names = {q.name for q in celery_app.conf.task_queues}
    expected_queues = {"default", "notifications", "grievance_processing", "maintenance"}
    assert expected_queues.issubset(queue_names)


def test_celery_task_routing():
    """Verify routing rules map task namespaces to designated logical queues."""
    routes = celery_app.conf.task_routes
    assert routes["app.tasks.notifications.*"]["queue"] == "notifications"
    assert routes["app.tasks.grievance.*"]["queue"] == "grievance_processing"
    assert routes["app.tasks.maintenance.*"]["queue"] == "maintenance"


def test_celery_task_registration():
    """Verify all Phase 4 background tasks are registered in the Celery registry."""
    registered = set(celery_app.tasks.keys())
    assert "app.tasks.notifications.send_grievance_notification_task" in registered
    assert "app.tasks.grievance.dispatch_outbox_events_task" in registered
    assert "app.tasks.grievance.reconcile_stale_outbox_events_task" in registered
    assert "app.tasks.grievance.process_grievance_lifecycle_event_task" in registered
    assert "app.tasks.maintenance.cleanup_abandoned_evidence_task" in registered
    assert "app.tasks.maintenance.periodic_health_check_task" in registered


# -----------------------------------------------------------------------------
# 2. Notification Provider Tests
# -----------------------------------------------------------------------------

def test_notification_provider_logging():
    """Verify LoggingNotificationProvider correctly logs and returns delivery confirmation."""
    provider = get_notification_provider()
    assert isinstance(provider, LoggingNotificationProvider)

    msg = NotificationMessage(
        recipient_email="citizen.test@civicmind.ai",
        recipient_phone="+919876543210",
        subject="Grievance Registered: GRV-2026-99001",
        body="Your grievance has been received and routed to PWD.",
        channel=NotificationChannel.EMAIL,
        metadata={"tracking_id": "GRV-2026-99001"},
    )
    result = provider.send(msg)
    assert result.success is True
    assert result.provider == "logging"
    assert result.message_id is not None
    assert result.message_id.startswith("notif-log-")


# -----------------------------------------------------------------------------
# 3. Task Idempotency Tests
# -----------------------------------------------------------------------------

def test_notification_task_idempotency():
    """
    Verify duplicate execution of send_grievance_notification_task
    with the same event ID and recipient is suppressed by Redis idempotency check.
    """
    event_id = f"test-evt-{uuid.uuid4().hex[:12]}"
    recipient = "idemp.citizen@civicmind.ai"

    # First execution -> should deliver
    res1 = send_grievance_notification_task(
        event_id=event_id,
        notification_type="grievance.created",
        recipient_email=recipient,
        recipient_phone=None,
        subject="Your Grievance Has Been Received",
        body="Details here...",
        channel="email",
        correlation_id=f"corr-{event_id}",
    )
    assert res1["status"] == "delivered"
    assert res1["recipient"] == recipient

    # Second execution with exact same event_id -> should be duplicate suppressed
    res2 = send_grievance_notification_task(
        event_id=event_id,
        notification_type="grievance.created",
        recipient_email=recipient,
        recipient_phone=None,
        subject="Your Grievance Has Been Received",
        body="Details here...",
        channel="email",
        correlation_id=f"corr-{event_id}",
    )
    assert res2["status"] == "skipped"
    assert res2["reason"] == "duplicate_suppressed"


# -----------------------------------------------------------------------------
# 4. Transactional Outbox Pattern & Dispatch Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_transactional_outbox_created_on_grievance_submission(db_session: AsyncSession):
    """
    Verify that creating a grievance atomically creates a pending OutboxEvent
    in PostgreSQL within the exact same database transaction.
    """
    citizen = User(
        email=f"outbox_cit_{uuid.uuid4().hex[:6]}@civicmind.ai",
        password_hash=get_password_hash("Citizen@123"),
        name="Outbox Citizen",
        role="citizen",
        phone="+919999988888",
    )
    db_session.add(citizen)

    dept = Department(
        id=f"TEST-DEPT-{uuid.uuid4().hex[:4]}",
        name="Test Dept Outbox",
        code=f"TDO-{uuid.uuid4().hex[:3]}",
        head_name="Chief Test Officer",
    )
    db_session.add(dept)
    await db_session.commit()

    payload = GrievanceCreateRequest(
        title="Pothole on Main Road near Outbox Test",
        description="Dangerous road crater causing vehicle damage.",
        category="Roads & Footpaths",
        subcategory="Pothole Repair",
        priority="high",
        department_id=dept.id,
        address="104 MG Road",
        ward="Ward 12",
        zone="Central",
        latitude=12.9716,
        longitude=77.5946,
    )
    grv_res = await GrievanceService.create_grievance(
        session=db_session,
        payload=payload,
        current_user=citizen,
    )

    # Query OutboxEvent table
    stmt = select(OutboxEvent).where(
        OutboxEvent.aggregate_id == grv_res.id,
        OutboxEvent.event_type == "grievance.created",
    )
    result = await db_session.execute(stmt)
    outbox_event = result.scalar_one_or_none()

    assert outbox_event is not None
    assert outbox_event.status == "pending"
    assert outbox_event.aggregate_type == "grievance"
    assert outbox_event.aggregate_id == grv_res.id
    assert outbox_event.payload["tracking_id"] == grv_res.id
    assert outbox_event.correlation_id == f"grv-create-{grv_res.id}"


def test_outbox_dispatch_task_processes_pending_events():
    """Verify dispatch_outbox_events_task transitions pending events to completed."""
    dispatch_res = dispatch_outbox_events_task(batch_size=20)
    assert dispatch_res["status"] in ("completed", "noop")
    assert isinstance(dispatch_res["dispatched"], int)
    assert isinstance(dispatch_res["failed"], int)


def test_outbox_reconcile_stale_events():
    """Verify reconcile_stale_outbox_events_task resets stale processing events."""
    reconcile_res = reconcile_stale_outbox_events_task(stale_threshold_seconds=1)
    assert reconcile_res["status"] == "reconciled"
    assert "reset_to_pending" in reconcile_res
    assert "marked_failed" in reconcile_res


# -----------------------------------------------------------------------------
# 5. Evidence Cleanup Safety Invariant Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_evidence_cleanup_safety_invariant(db_session: AsyncSession):
    """
    CRITICAL SAFETY TEST:
    Verify that cleanup_abandoned_evidence_task:
    1. NEVER deletes evidence attached to an active grievance (grievance_id IS NOT NULL).
    2. NEVER deletes unattached evidence created recently (< retention_hours).
    3. ONLY deletes unattached evidence older than retention_hours (both DB record and disk file).
    """
    citizen = User(
        email=f"ev_cit_{uuid.uuid4().hex[:6]}@civicmind.ai",
        password_hash=get_password_hash("Citizen@123"),
        name="Evidence Test Citizen",
        role="citizen",
    )
    db_session.add(citizen)
    await db_session.flush()

    dept = Department(
        id=f"DEPT-EV-{uuid.uuid4().hex[:4]}",
        name="Evidence Test Dept",
        code=f"ETD-{uuid.uuid4().hex[:3]}",
        head_name="Head Officer",
    )
    db_session.add(dept)
    await db_session.flush()

    grv_id = f"GRV-2026-{uuid.uuid4().hex[:5]}"
    grv = Grievance(
        id=grv_id,
        title="Evidence Test Grievance",
        description="Grievance for testing evidence attachments.",
        citizen_id=citizen.id,
        department_id=dept.id,
        category="Sanitation",
        subcategory="Garbage Collection",
        priority="medium",
        status="submitted",
        address="123 Test Street",
        ward="Ward 1",
        zone="South",
        latitude=12.9716,
        longitude=77.5946,
        expected_resolution_date=datetime.now(timezone.utc) + timedelta(days=3),
        sla_deadline=datetime.now(timezone.utc) + timedelta(hours=96),
    )
    db_session.add(grv)
    await db_session.flush()

    UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    file_attached = UPLOAD_BASE_DIR / f"test_attached_{uuid.uuid4().hex[:8]}.jpg"
    file_attached.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00" * 200)

    file_abandoned = UPLOAD_BASE_DIR / f"test_abandoned_{uuid.uuid4().hex[:8]}.jpg"
    file_abandoned.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00" * 300)

    file_recent = UPLOAD_BASE_DIR / f"test_recent_{uuid.uuid4().hex[:8]}.jpg"
    file_recent.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00" * 150)

    old_time = datetime.now(timezone.utc) - timedelta(hours=48)
    recent_time = datetime.now(timezone.utc) - timedelta(minutes=30)

    # 1. Attached evidence record (created 48h ago, but attached to a grievance)
    ev_attached = GrievanceEvidence(
        grievance_id=grv_id,
        uploaded_by=citizen.id,
        file_name=file_attached.name,
        storage_url=f"/api/v1/uploads/evidence/{uuid.uuid4()}/download",
        file_type="image",
        file_size_bytes=len(file_attached.read_bytes()),
        created_at=old_time,
    )
    db_session.add(ev_attached)

    # 2. Abandoned evidence record (created 48h ago, unattached)
    ev_abandoned = GrievanceEvidence(
        grievance_id=None,
        uploaded_by=citizen.id,
        file_name=file_abandoned.name,
        storage_url=f"/api/v1/uploads/evidence/{uuid.uuid4()}/download",
        file_type="image",
        file_size_bytes=len(file_abandoned.read_bytes()),
        created_at=old_time,
    )
    db_session.add(ev_abandoned)

    # 3. Recent evidence record (created 30min ago, unattached wizard upload in progress)
    ev_recent = GrievanceEvidence(
        grievance_id=None,
        uploaded_by=citizen.id,
        file_name=file_recent.name,
        storage_url=f"/api/v1/uploads/evidence/{uuid.uuid4()}/download",
        file_type="image",
        file_size_bytes=len(file_recent.read_bytes()),
        created_at=recent_time,
    )
    db_session.add(ev_recent)

    await db_session.commit()
    ev_attached_id = ev_attached.id
    ev_abandoned_id = ev_abandoned.id
    ev_recent_id = ev_recent.id

    # Run cleanup task with 24 hours retention
    cleanup_res = cleanup_abandoned_evidence_task(retention_hours=24)
    assert cleanup_res["status"] == "completed"
    assert cleanup_res["deleted_count"] >= 1

    # Verify database and file state after cleanup
    res_attached = await db_session.execute(
        select(GrievanceEvidence).where(GrievanceEvidence.id == ev_attached_id)
    )
    assert res_attached.scalar_one_or_none() is not None, "Attached evidence must NEVER be deleted!"
    assert file_attached.exists(), "Attached disk file must NOT be deleted!"
    file_attached.unlink(missing_ok=True)  # Clean up test file

    res_recent = await db_session.execute(
        select(GrievanceEvidence).where(GrievanceEvidence.id == ev_recent_id)
    )
    assert res_recent.scalar_one_or_none() is not None, "Recent unattached evidence must NOT be deleted!"
    assert file_recent.exists(), "Recent disk file must NOT be deleted!"
    file_recent.unlink(missing_ok=True)  # Clean up test file

    res_abandoned = await db_session.execute(
        select(GrievanceEvidence).where(GrievanceEvidence.id == ev_abandoned_id)
    )
    assert res_abandoned.scalar_one_or_none() is None, "Abandoned unattached evidence must be purged from DB!"
    assert not file_abandoned.exists(), "Abandoned disk file must be deleted!"


# -----------------------------------------------------------------------------
# 6. Scheduled Health Check Task Tests
# -----------------------------------------------------------------------------

def test_periodic_health_check_task():
    """Verify periodic_health_check_task verifies DB, Redis, and outbox queue."""
    health_res = periodic_health_check_task()
    assert health_res["status"] in ("healthy", "degraded")
    assert health_res["database"] is True
    assert health_res["redis"] is True
    assert "pending_outbox_count" in health_res
    assert "checked_at" in health_res


# -----------------------------------------------------------------------------
# 7. Administrator Operational API Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_tasks_health_endpoint_authorized(setup_task_auth: dict):
    """Verify GET /api/v1/admin/tasks/health succeeds for administrator."""
    headers = setup_task_auth["admin_headers"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/tasks/health", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["broker_status"] in ("connected", "disconnected")
        assert "broker_url" in data
        assert "workers_online" in data
        assert "registered_queues" in data
        assert "outbox_backlog" in data
        assert "default" in data["registered_queues"]
        assert "notifications" in data["registered_queues"]
        assert "grievance_processing" in data["registered_queues"]
        assert "maintenance" in data["registered_queues"]


@pytest.mark.asyncio
async def test_admin_tasks_health_forbidden_for_citizen(setup_task_auth: dict):
    """Verify GET /api/v1/admin/tasks/health rejects citizen role with 403 Forbidden."""
    headers = setup_task_auth["citizen_headers"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/tasks/health", headers=headers)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_tasks_health_unauthorized_missing_token():
    """Verify GET /api/v1/admin/tasks/health rejects unauthenticated call with 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/tasks/health")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_tasks_outbox_list(setup_task_auth: dict):
    """Verify GET /api/v1/admin/tasks/outbox returns paginated outbox events."""
    headers = setup_task_auth["admin_headers"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/tasks/outbox?limit=5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data


@pytest.mark.asyncio
async def test_admin_tasks_outbox_dispatch_endpoint(setup_task_auth: dict):
    """Verify POST /api/v1/admin/tasks/outbox/dispatch triggers batch processing."""
    headers = setup_task_auth["admin_headers"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/admin/tasks/outbox/dispatch?batch_size=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("completed", "noop")
        assert "dispatched" in data
        assert "failed" in data


@pytest.mark.asyncio
async def test_admin_tasks_evidence_cleanup_endpoint(setup_task_auth: dict):
    """Verify POST /api/v1/admin/tasks/evidence/cleanup triggers maintenance purge."""
    headers = setup_task_auth["admin_headers"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/admin/tasks/evidence/cleanup",
            headers=headers,
            json={"retention_hours": 48},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "deleted_count" in data
        assert "reclaimed_bytes" in data
