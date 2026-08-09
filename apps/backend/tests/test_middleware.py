"""Tests for request-ID, security headers, and rate-limiting middleware."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import RateLimitMiddleware
from app.core.ratelimit import InMemorySlidingWindowRateLimiter
from app.main import app as main_app

client = TestClient(main_app)


def test_request_id_is_echoed() -> None:
    """A client-supplied X-Request-ID must be returned on the response."""
    response = client.get("/healthz", headers={"X-Request-ID": "test-123"})
    assert response.headers["x-request-id"] == "test-123"


def test_request_id_is_generated_when_missing() -> None:
    """Requests without an ID must receive a generated one."""
    response = client.get("/healthz")
    assert response.headers["x-request-id"]


def test_security_headers_present() -> None:
    """Every response must carry the security hardening headers."""
    response = client.get("/healthz")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in response.headers


def test_rate_limit_returns_429() -> None:
    """Exceeding the configured limit must yield 429 with Retry-After."""
    test_app = FastAPI()
    test_app.add_middleware(
        RateLimitMiddleware,
        limiter=InMemorySlidingWindowRateLimiter(max_requests=2, window_seconds=60),
    )

    @test_app.get("/limited")
    def limited() -> dict[str, str]:
        """Echo an OK payload."""
        return {"ok": "true"}

    limited_client = TestClient(test_app)
    assert limited_client.get("/limited").status_code == 200
    assert limited_client.get("/limited").status_code == 200
    third = limited_client.get("/limited")
    assert third.status_code == 429
    assert "retry-after" in third.headers
