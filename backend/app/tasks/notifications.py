"""
CivicMind AI — Notification Background Tasks
"""

import logging
import uuid
from typing import Any, Dict, Optional
import redis
from app.core.celery_app import celery_app
from app.core.config import settings
from app.services.notifications.provider import (
    NotificationChannel,
    NotificationMessage,
    get_notification_provider,
)

logger = logging.getLogger("civicmind.tasks.notifications")


@celery_app.task(
    bind=True,
    name="app.tasks.notifications.send_grievance_notification_task",
    queue="notifications",
    max_retries=3,
    default_retry_delay=10,
    retry_backoff=True,
    retry_jitter=True,
)
def send_grievance_notification_task(
    self,
    event_id: str,
    notification_type: str,
    recipient_email: Optional[str],
    recipient_phone: Optional[str],
    subject: str,
    body: str,
    channel: str = "email",
    metadata: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Idempotent background notification delivery task.
    Prevents duplicate delivery across worker retries using Redis idempotency keys.
    """
    task_id = self.request.id or f"sync-{uuid.uuid4().hex[:8]}"
    metadata = metadata or {}
    recipient = recipient_email or recipient_phone or "unknown"
    idemp_key = f"civicmind:idemp:notif:{event_id}:{recipient}:{notification_type}"

    logger.info(
        "[TASK_START] task_id=%s task_name=%s correlation_id=%s recipient=%s type=%s",
        task_id,
        self.name,
        correlation_id,
        recipient,
        notification_type,
    )

    # 1. Idempotency Check via Redis SET NX with 24h expiration
    try:
        r = redis.from_url(settings.redis_connection_url)
        is_new = r.set(idemp_key, task_id, ex=86400, nx=True)
        if not is_new:
            logger.warning(
                "[TASK_DUPLICATE_SKIPPED] task_id=%s idemp_key=%s already processed",
                task_id,
                idemp_key,
            )
            return {
                "status": "skipped",
                "reason": "duplicate_suppressed",
                "idempotency_key": idemp_key,
                "correlation_id": correlation_id,
            }
    except Exception as ex:
        logger.warning(
            "[IDEMPOTENCY_CHECK_FAILED] task_id=%s could not verify Redis key: %s (proceeding with delivery)",
            task_id,
            ex,
        )

    # 2. Dispatch via Notification Provider
    try:
        provider = get_notification_provider()
        channel_enum = NotificationChannel(channel.lower()) if channel in ("email", "sms", "in_app") else NotificationChannel.EMAIL
        
        msg = NotificationMessage(
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            subject=subject,
            body=body,
            channel=channel_enum,
            metadata={**metadata, "correlation_id": correlation_id, "task_id": task_id},
        )
        
        result = provider.send(msg)
        
        logger.info(
            "[TASK_SUCCESS] task_id=%s provider=%s message_id=%s recipient=%s",
            task_id,
            result.provider,
            result.message_id,
            recipient,
        )
        
        return {
            "status": "delivered",
            "provider": result.provider,
            "message_id": result.message_id,
            "recipient": recipient,
            "correlation_id": correlation_id,
        }
    except Exception as exc:
        logger.error(
            "[TASK_FAILURE] task_id=%s error=%s (attempt %d/%d)",
            task_id,
            str(exc),
            self.request.retries + 1,
            self.max_retries,
        )
        raise self.retry(exc=exc)
