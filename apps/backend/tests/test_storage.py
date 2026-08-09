"""Storage service tests using an explicit in-memory fake."""

from app.infra.storage import StorageService


class FakeMediaStorage:
    """In-memory stand-in for the object-storage backend (test mock)."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}

    def upload(self, path: str, data: bytes, content_type: str) -> str:
        """Store bytes in memory and return the path."""
        self._objects[path] = data
        return path

    def download(self, path: str) -> bytes:
        """Return previously stored bytes."""
        return self._objects[path]

    def get_public_url(self, path: str) -> str:
        """Return a synthetic public URL."""
        return f"https://media.example.test/{path}"


def test_upload_fetch_and_url_roundtrip() -> None:
    """Uploading, fetching, and URL generation must behave consistently."""
    storage = StorageService(storage=FakeMediaStorage())
    path = storage.upload_media("images/photo.png", b"png-bytes", "image/png")
    assert storage.fetch_media(path) == b"png-bytes"
    assert storage.public_url(path) == "https://media.example.test/images/photo.png"
