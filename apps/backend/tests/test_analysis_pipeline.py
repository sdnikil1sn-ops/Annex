"""Pipeline tests with fake LLM/search and a real database."""

import json
import os
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.models.claim import Claim
from app.models.user import User
from app.services.analysis_pipeline import AnalysisPipelineService

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL not set",
)


class FakeLLM:
    def __init__(self, extraction: dict, verdict: dict) -> None:
        self._extraction = extraction
        self._verdict = verdict

    def complete_json(self, system: str, user: str) -> str:
        payload = self._extraction if "Extract" in system else self._verdict
        return json.dumps(payload)


class FakeSearch:
    def find_sources(self, text: str) -> list:
        return []


def test_pipeline_extracts_and_completes(db_session: Session) -> None:
    user = User(email=f"pipe-{uuid4().hex}@example.com")
    db_session.add(user)
    db_session.flush()
    analysis = Analysis(
        user_id=user.id,
        type=AnalysisType.TEXT,
        input_payload={"text": "The moon is made of cheese."},
        status=AnalysisStatus.PENDING,
    )
    db_session.add(analysis)
    db_session.flush()

    pipeline = AnalysisPipelineService(
        session=db_session,
        llm=FakeLLM(
            {"claims": [{"claim_text": "The moon is made of cheese.", "confidence": 80}]},
            {"status": "disputed", "summary": "No.", "confidence": 90, "sources": []},
        ),
        search=FakeSearch(),
    )
    pipeline.run(analysis)
    db_session.commit()

    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.credibility_score == 90
    claims = db_session.query(Claim).filter_by(analysis_id=analysis.id).all()
    assert len(claims) == 1
    assert claims[0].claim_text == "The moon is made of cheese."
