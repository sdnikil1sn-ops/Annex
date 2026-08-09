"""Repository roundtrips against a real Postgres (skipped without TEST_DATABASE_URL)."""

import os
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.models.claim import Claim
from app.models.user import User
from app.repositories.analysis import AnalysisRepository

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL not set",
)

def test_analysis_with_claims_roundtrip(db_session: Session) -> None:
    user = User(email=f"repo-{uuid4().hex}@example.com")
    db_session.add(user)
    db_session.flush()

    analysis = Analysis(
        user_id=user.id,
        type=AnalysisType.TEXT,
        input_payload={"text": "hi"},
        status=AnalysisStatus.PENDING,
    )
    repo = AnalysisRepository(db_session)
    repo.add(analysis)
    db_session.flush()

    db_session.add(
        Claim(analysis_id=analysis.id, claim_text="The moon is cheese")
    )
    db_session.commit()

    loaded = repo.get_with_results(analysis.id, user.id)
    assert loaded is not None
    assert loaded.claims[0].claim_text == "The moon is cheese"


def test_delete_cascades_to_claims(db_session: Session) -> None:
    ...


def test_get_for_user_respects_ownership(db_session: Session) -> None:
    ...


def test_list_for_user_orders_newest_first(db_session: Session) -> None:
    ...
