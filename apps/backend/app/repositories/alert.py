"""Repository for the Alert model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.repository import Repository
from app.models.alert import Alert


class AlertRepository(Repository[Alert]):
    """Ownership-scoped queries for alerts."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Alert)

    def list_for_user(self, user_id: UUID) -> list[Alert]:
        stmt = (
            select(Alert)
            .where(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
        )
        return list(self._session.scalars(stmt).all())

    def get_for_user(self, alert_id: UUID, user_id: UUID) -> Alert | None:
        stmt = select(Alert).where(
            Alert.id == alert_id,
            Alert.user_id == user_id,
        )
        return self._session.scalars(stmt).first()
