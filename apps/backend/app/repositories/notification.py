"""Repository for the Notification model."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.repository import Repository
from app.models.notification import Notification


class NotificationRepository(Repository[Notification]):
    """Queries for notifications."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Notification)

    def list_for_user(self, user_id: UUID) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
        )
        return list(self._session.scalars(stmt).all())

    def unread_count(self, user_id: UUID) -> int:
        stmt = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        return int(self._session.scalar(stmt) or 0)

    def get_for_user(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return self._session.scalars(stmt).first()

    def mark_all_read(self, user_id: UUID) -> None:
        notifications = self.list_for_user(user_id)
        for notification in notifications:
            notification.is_read = True
