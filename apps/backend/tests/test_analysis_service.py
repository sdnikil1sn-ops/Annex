"""Tests for the analysis service (in-memory repository)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.core.errors import NotFoundError
from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.schemas.analysis import AnalysisCreate, AnalysisInput
from app.services.analysis import AnalysisService


class FakeAnalysisRepository:
    """In-memory AnalysisRepositoryProtocol implementation."""

    def __init__(self) -> None:
        self._items: dict[str, Analysis] = {}

    def add(self, analysis: Analysis) -> Analysis:
        self._items[str(analysis.id)] = analysis
        return analysis

    def list_for_user(self, user_id: object) -> list[Analysis]:
        return [a for a in self._items.values() if a.user_id == user_id]

    def get_for_user(self, analysis_id: object, user_id: object) -> Analysis | None:
        item = self._items.get(str(analysis_id))
        return item if item is not None and item.user_id == user_id else None

    def get_with_results(self, analysis_id: object, user_id: object) -> Analysis | None:
        return self.get_for_user(analysis_id, user_id)

    def delete(self, analysis: Analysis) -> None:
        self._items.pop(str(analysis.id), None)
    
    def flush(self) -> None:
        pass
        
    def commit(self) -> None:
        pass


def make_analysis(user_id: object) -> Analysis:
    return Analysis(
        id=uuid4(),
        user_id=user_id,
        type=AnalysisType.TEXT,
        input_payload={"text": "hello"},
        status=AnalysisStatus.PENDING,
        created_at=datetime.now(UTC),
    )


def make_service() -> tuple[AnalysisService, FakeAnalysisRepository]:
    repo = FakeAnalysisRepository()
    return AnalysisService(repo), repo


def test_create_sets_pending_status() -> None:
    service, _ = make_service()
    user_id = uuid4()
    payload = AnalysisCreate(
        type=AnalysisType.TEXT,
        input_payload=AnalysisInput(text="hello"),
    )
    analysis = service.create(user_id, payload)
    assert analysis.status == AnalysisStatus.PENDING
    assert analysis.input_payload == {"text": "hello"}


def test_list_is_scoped_to_user() -> None:
    service, repo = make_service()
    alice, bob = uuid4(), uuid4()
    repo.add(make_analysis(alice))
    repo.add(make_analysis(alice))
    repo.add(make_analysis(bob))
    assert len(service.list_for_user(alice)) == 2


def test_get_raises_not_found_for_foreign_id() -> None:
    service, repo = make_service()
    repo.add(make_analysis(uuid4()))
    with pytest.raises(NotFoundError):
        service.get_for_user(uuid4(), uuid4())


def test_delete_removes_analysis() -> None:
    service, repo = make_service()
    user_id = uuid4()
    analysis = make_analysis(user_id)
    repo.add(analysis)
    service.delete_for_user(analysis.id, user_id)
    assert service.list_for_user(user_id) == []
