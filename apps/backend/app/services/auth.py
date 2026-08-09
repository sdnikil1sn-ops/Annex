"""Authentication service: Firebase token verification and user resolution."""

from functools import lru_cache
from typing import Any, Protocol

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.db.session import get_db
from app.infra.firebase import FirebaseIdTokenVerifier
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


class IdTokenVerifier(Protocol):
    """Interface for verifying Firebase ID tokens."""

    def verify(self, token: str) -> dict[str, Any]:
        """Return verified token claims for a raw ID token."""
        ...


class AuthService:
    """Resolves Firebase identity into an ANNEX user."""

    def __init__(self, verifier: IdTokenVerifier) -> None:
        self._verifier = verifier

    def authenticate(self, token: str) -> dict[str, Any]:
        """Verify a token and return normalized user claims."""
        claims = self._verifier.verify(token)
        uid = claims.get("uid")
        if not uid:
            raise UnauthorizedError("Token is missing a user identifier.")
        return {
            "uid": str(uid),
            "email": claims.get("email"),
            "name": claims.get("name") or claims.get("email"),
        }

    def ensure_user(self, db: Session, claims: dict[str, Any]) -> User:
        """Return the ANNEX user for claims, creating or linking as needed."""
        uid = claims["uid"]
        user = db.scalars(select(User).where(User.firebase_uid == uid)).one_or_none()
        if user is not None:
            return user

        email = claims.get("email")
        if email:
            user = db.scalars(select(User).where(User.email == email)).one_or_none()
            if user is not None:
                user.firebase_uid = uid
                db.commit()
                return user

        user = User(
            email=email or f"{uid}@users.annex.invalid",
            display_name=claims.get("name"),
            firebase_uid=uid,
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            # A concurrent request created the same user; reload by uid.
            db.rollback()
            user = db.scalars(select(User).where(User.firebase_uid == uid)).one_or_none()
            if user is None:
                raise
        return user


@lru_cache
def get_auth_service() -> AuthService:
    """Return the process-wide auth service backed by Firebase."""
    return AuthService(verifier=FirebaseIdTokenVerifier())


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> dict[str, Any]:
    """Verify the bearer token without touching the database."""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Missing bearer token.")
    return auth.authenticate(credentials.credentials)


def get_current_user(
    claims: dict[str, Any] = Depends(verify_token),
    db: Session = Depends(get_db),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    """Resolve the authenticated user from verified token claims."""
    return auth.ensure_user(db, claims)
