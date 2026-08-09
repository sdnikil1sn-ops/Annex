"""Authentication endpoint and service tests."""

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.main import app as main_app
from app.models.user import User
from app.services.auth import AuthService, get_auth_service, get_current_user


class FakeVerifier:
    """Test double for the Firebase ID-token verifier (test mock)."""

    def __init__(self, claims: dict[str, Any] | None = None, *, fail: bool = False) -> None:
        self._claims = claims or {}
        self._fail = fail

    def verify(self, token: str) -> dict[str, Any]:
        """Return fixed claims or raise for invalid-token scenarios."""
        if self._fail:
            raise UnauthorizedError("Invalid token.")
        return self._claims


def test_me_requires_token() -> None:
    """GET /api/v1/users/me without a token must return 401."""
    client = TestClient(main_app)
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_me_with_invalid_token() -> None:
    """GET /api/v1/users/me with a bad token must return 401."""
    auth = AuthService(verifier=FakeVerifier(fail=True))
    main_app.dependency_overrides[get_auth_service] = lambda: auth
    try:
        client = TestClient(main_app)
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
    finally:
        main_app.dependency_overrides.clear()


def test_me_returns_profile() -> None:
    """An authenticated user must receive their profile."""
    fake_user = User(id=uuid4(), email="alex@example.com", display_name="Alex")
    main_app.dependency_overrides[get_current_user] = lambda: fake_user
    try:
        client = TestClient(main_app)
        response = client.get("/api/v1/users/me")
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "alex@example.com"
        assert body["display_name"] == "Alex"
    finally:
        main_app.dependency_overrides.clear()


def test_authenticate_maps_claims() -> None:
    """authenticate must normalize verified claims."""
    verifier = FakeVerifier({"uid": "u1", "email": "a@b.co", "name": "A"})
    claims = AuthService(verifier=verifier).authenticate("tok")
    assert claims == {"uid": "u1", "email": "a@b.co", "name": "A"}


def test_authenticate_rejects_missing_uid() -> None:
    """Tokens without a uid must be rejected."""
    verifier = FakeVerifier({"email": "a@b.co"})
    with pytest.raises(UnauthorizedError):
        AuthService(verifier=verifier).authenticate("tok")


def test_authenticate_rejects_invalid_token() -> None:
    """Invalid tokens must raise UnauthorizedError."""
    verifier = FakeVerifier(fail=True)
    with pytest.raises(UnauthorizedError):
        AuthService(verifier=verifier).authenticate("tok")


def test_ensure_user_creates_and_links(db_session: Session) -> None:
    """ensure_user must link an existing email user and create new users."""
    auth = AuthService(verifier=FakeVerifier())
    suffix = uuid4().hex
    link_email = f"link-{suffix}@example.com"
    fresh_email = f"fresh-{suffix}@example.com"
    uid_one = f"fire-{suffix}"
    uid_two = f"fire2-{suffix}"

    existing = User(email=link_email, display_name="Link")
    db_session.add(existing)
    db_session.commit()

    linked = auth.ensure_user(
        db_session,
        {"uid": uid_one, "email": link_email, "name": "Link"},
    )
    assert linked.firebase_uid == uid_one

    fresh = auth.ensure_user(
        db_session,
        {"uid": uid_two, "email": fresh_email, "name": "New"},
    )
    assert fresh.firebase_uid == uid_two
