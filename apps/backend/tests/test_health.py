"""Integration tests for the health-check endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_reports_ok() -> None:
    """GET /healthz must return 200 with status and version."""
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"]
    assert payload["environment"]


def test_versioned_health_reports_ok() -> None:
    """GET /api/v1/health must mirror the liveness payload."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_points_to_docs() -> None:
    """GET / must link to the interactive OpenAPI documentation."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"
