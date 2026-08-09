"""Object-storage integration (Supabase Storage) with an injectable protocol."""

from typing import Any, Protocol, cast

from app.core.config import get_settings


class MediaStorage(Protocol):
    """Interface implemented by the object-storage backend."""

    def upload(self, path: str, data: bytes, content_type: str) -> str:
        """Upload bytes to ``path`` and return the stored path."""
        ...

    def download(self, path: str) -> bytes:
        """Download and return the bytes stored at ``path``."""
        ...

    def get_public_url(self, path: str) -> str:
        """Return the public URL for the object at ``path``."""
        ...


class SupabaseMediaStorage:
    """Supabase Storage implementation backed by the supabase-py client."""

    def __init__(self, client: Any, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def upload(self, path: str, data: bytes, content_type: str) -> str:
        """Upload bytes to Supabase Storage and return the stored path."""
        self._client.storage.from_(self._bucket).upload(
            path,
            data,
            file_options={"content-type": content_type},
        )
        return path

    def download(self, path: str) -> bytes:
        """Download bytes from Supabase Storage."""
        return cast(bytes, self._client.storage.from_(self._bucket).download(path))

    def get_public_url(self, path: str) -> str:
        """Return the public URL for an object in Supabase Storage."""
        return cast(str, self._client.storage.from_(self._bucket).get_public_url(path))


class StorageService:
    """High-level media storage service used by application code."""

    def __init__(self, storage: MediaStorage) -> None:
        self._storage = storage

    def upload_media(self, path: str, data: bytes, content_type: str) -> str:
        """Store a media blob and return its path within the bucket."""
        return self._storage.upload(path, data, content_type)

    def fetch_media(self, path: str) -> bytes:
        """Return the bytes of a stored media blob."""
        return self._storage.download(path)

    def public_url(self, path: str) -> str:
        """Return the public URL for a stored media blob."""
        return self._storage.get_public_url(path)


def build_storage_service() -> StorageService:
    """Build the default storage service from application settings."""
    from supabase import create_client

    settings = get_settings()
    client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
    storage = SupabaseMediaStorage(client=client, bucket=settings.storage_bucket)
    return StorageService(storage=storage)
