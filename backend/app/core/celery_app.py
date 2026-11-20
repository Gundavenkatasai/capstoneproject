"""
CivicMind AI — Celery Distributed Task Processing Application
Configures Redis broker, result backend, task queues, routing, and Celery Beat schedule.
"""

import logging
from celery import Celery
from kombu import Queue, Exchange
from app.core.config import settings

logger = logging.getLogger("civicmind.celery")

# Initialize Celery app
celery_app = Celery("civicmind_tasks")

# Define Exchanges
default_exchange = Exchange("default", type="direct")
notifications_exchange = Exchange("notifications", type="direct")
grievance_exchange = Exchange("grievance_processing", type="direct")
maintenance_exchange = Exchange("maintenance", type="direct")

# Celery Configuration
celery_app.conf.update(
    # Broker & Backend
    broker_url=settings.celery_broker,
    result_backend=settings.celery_backend,
    
    # Task serialization (Strict JSON security)
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    
    # Timezone & Scheduling
    timezone="UTC",
    enable_utc=True,
    
    # Task Execution Guarantees
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    result_expires=settings.CELERY_RESULT_EXPIRES,
    
    # Testing & Synchronous Override
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
    
    # Worker Concurrency & Prefetch
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_prefetch_multiplier=1,
    
    # Logical Task Queues
    task_queues=[
        Queue("default", default_exchange, routing_key="default"),
        Queue("notifications", notifications_exchange, routing_key="notifications"),
        Queue("grievance_processing", grievance_exchange, routing_key="grievance_processing"),
        Queue("maintenance", maintenance_exchange, routing_key="maintenance"),
    ],
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Task Routing
    task_routes={
        "app.tasks.notifications.*": {"queue": "notifications", "routing_key": "notifications"},
        "app.tasks.grievance.*": {"queue": "grievance_processing", "routing_key": "grievance_processing"},
        "app.tasks.maintenance.*": {"queue": "maintenance", "routing_key": "maintenance"},
    },
    
    # Celery Beat Scheduled Tasks
    beat_schedule={
        "dispatch-outbox-events-every-15s": {
            "task": "app.tasks.grievance.dispatch_outbox_events_task",
            "schedule": 15.0,  # every 15 seconds
            "options": {"queue": "grievance_processing"},
        },
        "reconcile-stale-outbox-every-5m": {
            "task": "app.tasks.grievance.reconcile_stale_outbox_events_task",
            "schedule": 300.0,  # every 5 minutes
            "options": {"queue": "grievance_processing"},
        },
        "cleanup-abandoned-evidence-daily": {
            "task": "app.tasks.maintenance.cleanup_abandoned_evidence_task",
            "schedule": 3600.0 * 24,  # daily
            "options": {"queue": "maintenance"},
        },
        "periodic-health-check-every-5m": {
            "task": "app.tasks.maintenance.periodic_health_check_task",
            "schedule": 300.0,  # every 5 minutes
            "options": {"queue": "maintenance"},
        },
    },
)

# Autodiscover tasks from registered task modules
celery_app.autodiscover_tasks([
    "app.tasks.notifications",
    "app.tasks.grievance",
    "app.tasks.maintenance",
])
