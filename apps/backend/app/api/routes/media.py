"""Media upload endpoints (authenticated)."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_media_storage
from app.infra.storage import MediaStorage
from app.models.user import User
from app.schemas.media import MediaUploadResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_media(
    file: UploadFile = File(...),  # noqa: B008
    current_user: User = Depends(get_current_user),
    storage: MediaStorage = Depends(get_media_storage),
) -> MediaUploadResponse:
    """Upload a media file and return its storage path + public URL."""
    ext = Path(file.filename or "file").suffix.lower()
    path = f"users/{current_user.id}/{uuid.uuid4().hex}{ext}"
    data = file.file.read()
    storage.upload(path, data, file.content_type or "application/octet-stream")
    return MediaUploadResponse(path=path, url=storage.get_public_url(path))
