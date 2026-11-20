# CivicMind AI — Phase 4 Implementation Report
## Background Processing Infrastructure & Distributed Task Engine

**Document Status**: COMPLETED  
**Implementation Phase**: Phase 4  
**Date**: November 20, 2026  
**Repository Branch**: `main`  
**Test Suite Status**: 86 / 86 tests passed (100% pass rate)

---

## 1. Executive Summary

Phase 4 of the CivicMind AI platform establishes a production-grade, distributed asynchronous task processing infrastructure powered by **Celery 5.7** and **Redis 7**. 

The system decouples high-latency, multi-step, and scheduled operations from FastAPI request handlers while guaranteeing database-to-broker consistency using the **Transactional Outbox Pattern** in PostgreSQL 16. Operations such as citizen notification dispatch, abandoned evidence purging, stale event reconciliation, and periodic operational health monitoring now execute asynchronously with strict idempotency and bounded exponential backoff retries.

---

## 2. Architecture & Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI HTTP Gateway                              │
│                                                                             │
│   Citizen / Officer / Admin Request (e.g. POST /api/v1/grievances)          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL ACID Transaction Boundary                     │
│                                                                             │
│   1. Insert/Update Grievance, Timeline, AuditLog                            │
│   2. Insert OutboxEvent (status='pending', scheduled_for=now())             │
│   3. COMMIT (Atomic: Both entity and outbox succeed or roll back together)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Celery Beat Scheduler & Outbox Dispatcher                 │
│                                                                             │
│   Task: app.tasks.grievance.dispatch_outbox_events_task (every 15s)         │
│   - SELECT ... FOR UPDATE SKIP LOCKED (batch_size=50)                       │
│   - Mark status = 'processing', increment attempts                          │
│   - Publish task to designated Celery Queue                                 │
│   - Mark status = 'completed'                                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           ▼                           ▼                           ▼
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│    notifications     │   │ grievance_processing │   │     maintenance      │
│        Queue         │   │        Queue         │   │        Queue         │
└──────────┬───────────┘   └──────────┬───────────┘   └──────────┬───────────┘
           │                          │                          │
           ▼                          ▼                          ▼
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│ send_grievance_      │   │ process_grievance_   │   │ cleanup_abandoned_   │
│ notification_task    │   │ lifecycle_event_task │   │ evidence_task        │
│ (Redis Idempotency)  │   │                      │   │ periodic_health_     │
│                      │   │ reconcile_stale_     │   │ check_task           │
│                      │   │ outbox_events_task   │   │                      │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

---

## 3. Queue Topology & Routing Rules

Celery is configured with 4 dedicated logical queues using direct exchanges to prevent high-frequency tasks from starving mission-critical lifecycle jobs:

| Queue Name | Exchange | Routing Key | Task Modules / Patterns | SLA / Priority |
| :--- | :--- | :--- | :--- | :--- |
| `notifications` | `notifications` | `notifications` | `app.tasks.notifications.*` | Near real-time citizen & officer alerts |
| `grievance_processing` | `grievance_processing` | `grievance_processing` | `app.tasks.grievance.*` | Outbox polling, lifecycle side-effects, reconciliation |
| `maintenance` | `maintenance` | `maintenance` | `app.tasks.maintenance.*` | File purging, integrity checks, hourly/daily cron |
| `default` | `default` | `default` | Generic/unrouted tasks | Baseline catch-all |

### Serialization & Security
- **Task Serialization**: JSON only (`task_serializer="json"`, `result_serializer="json"`, `accept_content=["json"]`). Pickle is strictly forbidden.
- **Timezone**: Strict UTC scheduling (`enable_utc=True`, `timezone="UTC"`).
- **Execution Limits**: Hard time limit of 300 seconds (5 min), soft time limit of 240 seconds (4 min).
- **Worker Prefetch**: Set to `worker_prefetch_multiplier = 1` for fair round-robin dispatch across workers.

---

## 4. Transactional Outbox Pattern & Consistency Strategy

### The Problem Solved
In distributed systems, publishing a Celery/Redis task directly inside an HTTP handler risks dual-write split-brain:
1. **Ghost Tasks**: A Celery task is published to Redis, but the PostgreSQL transaction subsequently fails or rolls back. The worker acts on non-existent data.
2. **Lost Tasks**: The database transaction commits, but the worker or network fails before publishing to Redis. The downstream task is lost forever.

### The CivicMind Implementation
All grievance lifecycle events (`create_grievance`, `transition_status`, `submit_resolution`, `verify_resolution`, `submit_appeal`) write an `OutboxEvent` record in the **exact same SQLAlchemy session** before `await session.commit()`.

#### Database Schema: `outbox_events` (Migration `0005_outbox_events`)
- `id`: UUID (Primary Key)
- `event_type`: `VARCHAR(100)` (e.g. `grievance.created`, `grievance.status_changed`, `grievance.resolved`)
- `aggregate_type`: `VARCHAR(50)` (default: `'grievance'`)
- `aggregate_id`: `VARCHAR(100)` (Foreign tracking ID / UUID)
- `payload`: `JSONB` (Complete serializable event payload)
- `status`: `VARCHAR(20)` (`pending`, `processing`, `completed`, `failed`)
- `attempts`: `INTEGER` (Current delivery attempts)
- `max_attempts`: `INTEGER` (Ceiling, default: 5)
- `correlation_id`: `VARCHAR(100)` (Traces causality across services)
- `error_details`: `TEXT` (Captures stack traces on delivery failure)
- `scheduled_for`: `TIMESTAMPTZ` (Enables delayed/backoff dispatch)
- `processed_at`: `TIMESTAMPTZ` (Audit timestamp of successful delivery)
- `created_at` / `updated_at`: `TIMESTAMPTZ` (Auditing & stale detection)

#### Reconciliation & Anti-Entropy
`reconcile_stale_outbox_events_task` runs every 5 minutes. If a worker process dies mid-dispatch, events stuck in `'processing'` for longer than 300 seconds are safely reset to `'pending'` (if attempts < max_attempts) or marked `'failed'`.

---

## 5. Background Task Inventory

| Task Name | Queue | Schedule / Trigger | Description |
| :--- | :--- | :--- | :--- |
| `app.tasks.notifications.send_grievance_notification_task` | `notifications` | Triggered by lifecycle | Delivers citizen & officer notifications via pluggable providers with Redis idempotency. |
| `app.tasks.grievance.dispatch_outbox_events_task` | `grievance_processing` | Every 15 seconds / Manual API | Scans pending outbox records (`SELECT FOR UPDATE SKIP LOCKED`), dispatches Celery jobs, marks completed. |
| `app.tasks.grievance.reconcile_stale_outbox_events_task` | `grievance_processing` | Every 5 minutes | Recovers abandoned/stuck outbox records exceeding timeout thresholds. |
| `app.tasks.grievance.process_grievance_lifecycle_event_task` | `grievance_processing` | Dispatched from Outbox | Formats contextual notifications and queues delivery. |
| `app.tasks.maintenance.cleanup_abandoned_evidence_task` | `maintenance` | Daily / Manual API | Purges unattached evidence uploads older than configurable retention (default 24h). NEVER touches attached evidence. |
| `app.tasks.maintenance.periodic_health_check_task` | `maintenance` | Every 5 minutes | Assesses PostgreSQL and Redis liveness and monitors pending outbox backlog. |

---

## 6. Notification Provider Abstraction

Located in `app/services/notifications/provider.py`:
- `BaseNotificationProvider`: Abstract base class defining `send(message: NotificationMessage) -> NotificationResult`.
- `LoggingNotificationProvider`: Secure local logging provider that outputs structured log payloads (`[NOTIFICATION_DISPATCH]`) without transmitting external HTTP/SMTP traffic.
- **Pluggable Architecture**: Ready for SMTP (`SMTPNotificationProvider`) and SMS (`TwilioNotificationProvider`) without modifying task logic.
- **Idempotency Guard**: Every notification computes an idempotency key `civicmind:idemp:notif:{event_id}:{recipient}:{notification_type}` and stores it in Redis with `SET NX EX 86400`. Repeated execution attempts are immediately short-circuited as `duplicate_suppressed`.

---

## 7. Evidence Cleanup Invariant & Safety Proof

Unattached file uploads (e.g., from abandoned citizen wizards) consume disk space. However, active grievance evidence must never be corrupted.

The `cleanup_abandoned_evidence_task` enforces two strict safety invariants:
1. **Query Filter**: `WHERE grievance_id IS NULL AND created_at < cutoff`
2. **Runtime Code Assertion**: If `evidence.grievance_id is not None`, the file is immediately bypassed and logged as an integrity violation abort.
3. **Directory Traversal Guard**: Resolved file paths are verified to reside within `uploads/evidence/` before deletion.

---

## 8. Operational & Administrative Endpoints

Mounted under `/api/v1/admin/tasks` (Protected by `require_role(["admin"])`):

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/admin/tasks/health` | Broker connectivity, worker online status, queue registry, outbox backlog counts |
| `GET` | `/api/v1/admin/tasks/outbox` | Paginated listing of outbox events filterable by status and event type |
| `POST` | `/api/v1/admin/tasks/outbox/dispatch` | Immediate manual trigger to flush and dispatch pending outbox events |
| `POST` | `/api/v1/admin/tasks/evidence/cleanup` | Manual trigger for unattached evidence cleanup with configurable retention hours |

---

## 9. Verification & Automated Test Results

Test suite: `tests/test_tasks.py` + full regression across 12 test modules.

```bash
$ uv run pytest tests/ -v
======================= 86 passed, 3 warnings in 13.54s =======================
```

### Breakdown by Module:
- `test_tasks.py`: **16 passed** (Celery configuration, routing, registration, idempotency, outbox ACID, dispatch, stale recovery, evidence cleanup invariants, health checks, admin endpoints).
- `test_grievances.py`: **10 passed** (Phase 3 grievance lifecycle & ACID outbox event registration).
- `test_auth.py`: **23 passed** (JWT, Argon2id, Google SSO, token rotation).
- `test_rbac.py`: **6 passed** (Role-based access control, IDOR guards).
- `test_models.py`: **8 passed** (SQLAlchemy 2 schemas, Outbox table registration).
- `test_migrations.py`: **6 passed** (Alembic revisions 0001 through 0005).
- `test_database.py`: **4 passed** (Async & sync sessions, rollbacks).
- `test_pgvector.py`: **4 passed** (HNSW index, cosine vector distance).
- `test_health.py`: **4 passed** (Aggregate, DB, Redis probes).
- `test_redis.py`: **2 passed** (Blacklist & caching CRUD).
- `test_startup.py`: **3 passed** (FastAPI app & OpenAPI schema).

---

## 10. Manual Verification Commands

### Start Celery Worker:
```powershell
cd backend
uv run celery -A app.core.celery_app.celery_app worker --loglevel=info -Q default,notifications,grievance_processing,maintenance -c 4
```

### Start Celery Beat Scheduler:
```powershell
cd backend
uv run celery -A app.core.celery_app.celery_app beat --loglevel=info
```

### Trigger Outbox Dispatch via Admin API:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/admin/tasks/outbox/dispatch?batch_size=50" \
     -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```

### Trigger Evidence Cleanup:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/admin/tasks/evidence/cleanup" \
     -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"retention_hours": 24}'
```
