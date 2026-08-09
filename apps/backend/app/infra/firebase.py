"""Firebase Admin SDK initialization and ID-token verification."""

from typing import Any

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.config import get_settings


def _ensure_firebase() -> None:
    """Initialize the Firebase Admin SDK exactly once per process."""
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    settings = get_settings()
    credential = None
    if settings.firebase_service_account_path:
        credential = credentials.Certificate(settings.firebase_service_account_path)
    firebase_admin.initialize_app(
        credential=credential,
        options={"projectId": settings.firebase_project_id},
    )


class FirebaseIdTokenVerifier:
    """Verifies Firebase ID tokens using the Admin SDK public keys."""

    def verify(self, token: str) -> dict[str, Any]:
        """Return verified token claims for a raw Firebase ID token."""
        _ensure_firebase()
        decoded = firebase_auth.verify_id_token(token)
        return dict(decoded)
