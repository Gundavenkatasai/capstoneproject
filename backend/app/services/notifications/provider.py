"""
CivicMind AI — Notification Provider Abstraction
Provides pluggable providers for email, SMS, and in-app alerts.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
import logging
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger("civicmind.notifications")


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationMessage(BaseModel):
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    subject: str
    body: str
    channel: NotificationChannel = NotificationChannel.EMAIL
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationResult(BaseModel):
    success: bool
    provider: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    delivered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseNotificationProvider(ABC):
    """
    Abstract interface for notification dispatchers.
    """
    @abstractmethod
    def send(self, message: NotificationMessage) -> NotificationResult:
        """
        Deliver a notification message.
        """
        pass


class LoggingNotificationProvider(BaseNotificationProvider):
    """
    Development and audit notification provider that formats and logs notification
    payloads without sending outbound network requests.
    """
    def send(self, message: NotificationMessage) -> NotificationResult:
        msg_id = f"notif-log-{uuid.uuid4().hex[:12]}"
        logger.info(
            "[NOTIFICATION_DISPATCH] provider=logging msg_id=%s channel=%s recipient_email=%s recipient_phone=%s subject=%s body_preview=%.80s metadata=%s",
            msg_id,
            message.channel.value,
            message.recipient_email,
            message.recipient_phone,
            message.subject,
            message.body.replace("\n", " "),
            message.metadata,
        )
        return NotificationResult(
            success=True,
            provider="logging",
            message_id=msg_id,
        )


def get_notification_provider() -> BaseNotificationProvider:
    """
    Factory delivering the configured notification provider.
    """
    provider_name = settings.NOTIFICATION_PROVIDER.lower().strip()
    if provider_name in ("logging", "log", "console"):
        return LoggingNotificationProvider()
    # Default to LoggingNotificationProvider
    return LoggingNotificationProvider()
