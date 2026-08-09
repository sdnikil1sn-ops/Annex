"""Tests for the analysis API (no database)."""

from collections.abc import Iterator
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_analysis_service
from app.core.errors import NotFoundError
from app.main import app
from app.models.analysis import AnalysisType
from app.services.auth import get_current_user

client = TestClient(app)

USER_ID = uuid4()


class FakeAnalysisService:
    """In-memory stand-in for AnalysisService."""

    def __init__(self) -> None:
        self._items: dict[str, SimpleNamespace] = {}

    def create(self, user_id: object, payload: object) -> SimpleNamespace:
        item = SimpleNamespace(
            id=uuid4(),
            type=AnalysisType.TEXT,
            status="pending",
            input_payload={"text": "hello"},
            summary=None,
            credibility_score=None,
            created_at=datetime.now(UTC),
            claims=[],
        )
        self._items[str(item.id)] = item
        return item

    def list_for_user(self, user_id: object) -> list[SimpleNamespace]:
        return list(self._items.values())

    def get_with_results(self, analysis_id: object, user_id: object) -> SimpleNamespace:
        item = self._items.get(str(analysis_id))
        if item is None:
            raise NotFoundError("Analysis not found")
        return item

    def delete_for_user(self, analysis_id: object, user_id: object) -> None:
        self._items.pop(str(analysis_id), None)


def override_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=USER_ID,
        email="a@b.c",
        display_name=None,
        firebase_uid="uid",
    )


def override_service() -> FakeAnalysisService:
    return FakeAnalysisService()


def _no_enqueue(analysis_id: str) -> None:
    return None


@pytest.fixture(autouse=True)
def _scoped_overrides() -> Iterator[None]:
    """Install fakes before each test and clear them after (never leaks)."""
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_analysis_service] = override_service
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _no_real_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never dispatch a real Celery task from tests."""
    monkeypatch.setattr("app.api.routes.analyses._enqueue", _no_enqueue)


BASE = "/api/v1/analyses"


def test_create_returns_201() -> None:
    response = client.post(BASE, json={"type": "text", "input_payload": {"text": "hi"}})
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_list_returns_200() -> None:
    response = client.get(BASE)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_unknown_returns_404() -> None:
    response = client.get(f"{BASE}/{uuid4()}")
    assert response.status_code == 404


def test_delete_returns_204() -> None:
    created = client.post(BASE, json={"type": "text", "input_payload": {"text": "hi"}})
    analysis_id = created.json()["id"]
    response = client.delete(f"{BASE}/{analysis_id}")
    assert response.status_code == 204


def test_unauthenticated_returns_401() -> None:
    app.dependency_overrides.clear()
    response = client.get(BASE)
    assert response.status_code == 401
