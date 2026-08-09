"""Authenticated user endpoints."""

from fastapi import APIRouter, Depends

from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", summary="Get the authenticated user's profile")
def get_me(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    """Return the profile of the currently authenticated user."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name or "",
        "firebase_uid": current_user.firebase_uid or "",
    }
