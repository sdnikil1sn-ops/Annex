"""Media schemas."""

from pydantic import BaseModel


class MediaUploadResponse(BaseModel):
    """Result of a media upload: storage path + public URL."""

    path: str
    url: str
