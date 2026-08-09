"""Notification domain service."""

from typing import Protocol
from uuid import UUID

from app.core.errors import NotFoundError
from app.models.notification import Notification, NotificationType


class NotificationRepositoryProtocol(Protocol):
    def add(self, notification: Notification) -> Notification: ...
    def list_for_user(self, user_id: UUID) -> list[Notification]: ...
    def unread_count(self, user_id: UUID) -> int: ...
    def get_for_user(self, notification_id: UUID, user_id: UUID) -> Notification | None: ...
    def mark_all_read(self, user_id: UUID) -> None: ...


class NotificationService:
    """Create, list, and read notifications."""

    def __init__(self, notifications: NotificationRepositoryProtocol) -> None:
        self._notifications = notifications

    def create_notification(
        self,
        user_id: UUID,
        type: NotificationType,
        title: str,
        body: str | None = None,
    ) -> Notification:
        return self._notifications.add(
            Notification(user_id=user_id, type=type, title=title, body=body)
        )

    def list_for_user(self, user_id: UUID) -> list[Notification]:
        return self._notifications.list_for_user(user_id)

    def unread_count(self, user_id: UUID) -> int:
        return self._notifications.unread_count(user_id)

    def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notification = self._notifications.get_for_user(notification_id, user_id)
        if notification is None:
            raise NotFoundError("Notification not found")
        notification.is_read = True
        return notification

    def mark_all_read(self, user_id: UUID) -> None:
        self._notifications.mark_all_read(user_id)
