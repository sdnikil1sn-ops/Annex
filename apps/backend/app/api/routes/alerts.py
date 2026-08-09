"""Alert endpoints (authenticated, ownership-scoped)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_alert_service
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertRead, AlertUpdate
from app.services.alert import AlertService
from app.services.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: AlertCreate,
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    return service.create(  # type: ignore[return-value]
        current_user.id, payload.name, payload.query, payload.frequency
    )


@router.get("", response_model=list[AlertRead])
def list_alerts(
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> list[AlertRead]:
    return service.list_for_user(current_user.id)  # type: ignore[return-value]


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    return service.get_for_user(alert_id, current_user.id)  # type: ignore[return-value]


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: UUID,
    payload: AlertUpdate,
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    changes = payload.model_dump(exclude_unset=True)
    return service.update_for_user(alert_id, current_user.id, **changes)  # type: ignore[return-value]


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> Response:
    service.delete_for_user(alert_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
