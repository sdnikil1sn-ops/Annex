"""Eager Celery task tests (no broker, no OpenAI)."""

import os
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.models.user import User
from app.tasks.analysis import run_analysis_pipeline

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL not set",
)


class FakePipeline:
    """No-op pipeline stand-in."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.run = lambda analysis: None


@pytest.fixture()
def fake_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.tasks.analysis.AnalysisPipelineService", FakePipeline)


def test_task_is_registered() -> None:
    assert run_analysis_pipeline.name == "app.tasks.analysis.run_analysis_pipeline"


def test_task_runs_eagerly(fake_pipeline: None, db_session: Session) -> None:
    user = User(email=f"task-{uuid4().hex}@example.com")
    db_session.add(user)
    db_session.flush()
    analysis = Analysis(
        user_id=user.id,
        type=AnalysisType.TEXT,
        input_payload={"text": "hi"},
        status=AnalysisStatus.PENDING,
    )
    db_session.add(analysis)
    db_session.commit()

    run_analysis_pipeline.apply(args=[str(analysis.id)])

    db_session.expire_all()
    reloaded = db_session.get(Analysis, analysis.id)
    assert reloaded is not None
    assert reloaded.status == AnalysisStatus.PROCESSING
