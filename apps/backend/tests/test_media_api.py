"""Tests for the media upload API (no database)."""

from collections.abc import Iterator
from io import BytesIO
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_media_storage
from app.main import app
from app.services.auth import get_current_user

client = TestClient(app)

USER_ID = uuid4()


class FakeMediaStorage:
    def __init__(self) -> None:
        self._items: dict[str, bytes] = {}

    def upload(self, path: str, data: bytes, content_type: str) -> str:
        self._items[path] = data
        return path

    def download(self, path: str) -> bytes:
        return self._items[path]

    def get_public_url(self, path: str) -> str:
        return f"https://fake.storage/{path}"


def override_user() -> SimpleNamespace:
    return SimpleNamespace(id=USER_ID, email="a@b.c", display_name=None, firebase_uid="uid")


def override_storage() -> FakeMediaStorage:
    return FakeMediaStorage()


@pytest.fixture(autouse=True)
def _scoped_overrides() -> Iterator[None]:
    """Install fakes before each test and clear them after (never leaks)."""
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_media_storage] = override_storage
    yield
    app.dependency_overrides.clear()


def test_upload_returns_path_and_url() -> None:
    response = client.post(
        "/api/v1/media/upload",
        files={"file": ("photo.jpg", BytesIO(b"data"), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["path"].startswith(f"users/{USER_ID}/")
    assert body["url"].startswith("https://fake.storage/")


def test_upload_unauthenticated_returns_401() -> None:
    app.dependency_overrides.clear()
    try:
        response = client.post(
            "/api/v1/media/upload",
            files={"file": ("photo.jpg", BytesIO(b"data"), "image/jpeg")},
        )
        assert response.status_code == 401
    finally:
        app.dependency_overrides[get_current_user] = override_user
        app.dependency_overrides[get_media_storage] = override_storage
