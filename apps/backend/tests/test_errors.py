"""Tests for the global exception handlers."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import NotFoundError, register_exception_handlers
from app.core.middleware import RequestIDMiddleware

app_under_test = FastAPI()
app_under_test.add_middleware(RequestIDMiddleware)
register_exception_handlers(app_under_test)

# raise_server_exceptions=False: Starlette's ServerErrorMiddleware re-raises
# handled 500s so the server can log them; the TestClient propagates that by
# default, so we disable it to assert on the sanitized response body instead.


class Item(BaseModel):
    """Minimal body model for validation tests."""

    name: str


@app_under_test.get("/missing")
def missing() -> None:
    """Raise a typed not-found error."""
    raise NotFoundError("Resource not found")


@app_under_test.get("/boom")
def boom() -> None:
    """Raise an unexpected exception."""
    raise RuntimeError("internal secret detail")


@app_under_test.post("/items")
def create_item(item: Item) -> dict[str, str]:
    """Echo the validated item name."""
    return {"name": item.name}


client = TestClient(app_under_test, raise_server_exceptions=False)


def test_app_error_shape() -> None:
    """AppError must produce a structured JSON error envelope."""
    response = client.get("/missing")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "Resource not found"
    assert body["error"]["request_id"]


def test_unhandled_error_is_sanitized() -> None:
    """Unexpected exceptions must return a generic 500 without internals."""
    response = client.get("/boom")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "secret" not in body["error"]["message"]


def test_validation_error_shape() -> None:
    """Request validation failures must return a structured 422."""
    response = client.post("/items", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"]
