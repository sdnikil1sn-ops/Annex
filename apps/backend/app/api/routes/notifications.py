"""Notification endpoints (authenticated)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_notification_service
from app.models.user import User
from app.schemas.notification import NotificationRead, UnreadCountRead
from app.services.auth import get_current_user
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> list[NotificationRead]:
    return service.list_for_user(current_user.id)  # type: ignore[return-value]


@router.get("/unread-count", response_model=UnreadCountRead)
def unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> UnreadCountRead:
    return UnreadCountRead(count=service.unread_count(current_user.id))


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationRead:
    return service.mark_read(notification_id, current_user.id)  # type: ignore[return-value]


@router.patch("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> dict[str, str]:
    service.mark_all_read(current_user.id)
    return {"status": "ok"}
