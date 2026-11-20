"""
CivicMind AI — Notification Service Package
"""

from app.services.notifications.provider import (
    NotificationChannel,
    NotificationMessage,
    NotificationResult,
    BaseNotificationProvider,
    LoggingNotificationProvider,
    get_notification_provider,
)

__all__ = [
    "NotificationChannel",
    "NotificationMessage",
    "NotificationResult",
    "BaseNotificationProvider",
    "LoggingNotificationProvider",
    "get_notification_provider",
]
