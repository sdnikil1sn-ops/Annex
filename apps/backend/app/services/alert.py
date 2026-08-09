"""Alert domain service (ownership-scoped)."""

from typing import Protocol
from uuid import UUID

from app.core.errors import NotFoundError
from app.models.alert import Alert, AlertFrequency


class AlertRepositoryProtocol(Protocol):
    def add(self, alert: Alert) -> Alert: ...
    def list_for_user(self, user_id: UUID) -> list[Alert]: ...
    def get_for_user(self, alert_id: UUID, user_id: UUID) -> Alert | None: ...
    def delete(self, alert: Alert) -> None: ...


class AlertService:
    """CRUD for alerts."""

    def __init__(self, alerts: AlertRepositoryProtocol) -> None:
        self._alerts = alerts

    def create(
        self,
        user_id: UUID,
        name: str,
        query: dict[str, object],
        frequency: AlertFrequency,
    ) -> Alert:
        return self._alerts.add(Alert(user_id=user_id, name=name, query=query, frequency=frequency))

    def list_for_user(self, user_id: UUID) -> list[Alert]:
        return self._alerts.list_for_user(user_id)

    def get_for_user(self, alert_id: UUID, user_id: UUID) -> Alert:
        alert = self._alerts.get_for_user(alert_id, user_id)
        if alert is None:
            raise NotFoundError("Alert not found")
        return alert

    def update_for_user(self, alert_id: UUID, user_id: UUID, **changes: object) -> Alert:
        alert = self.get_for_user(alert_id, user_id)
        for key, value in changes.items():
            setattr(alert, key, value)
        return alert

    def delete_for_user(self, alert_id: UUID, user_id: UUID) -> None:
        self._alerts.delete(self.get_for_user(alert_id, user_id))
