"""Analysis domain service (ownership-scoped)."""

from typing import Protocol
from uuid import UUID

from app.core.errors import NotFoundError
from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.analysis import AnalysisCreate


class AnalysisRepositoryProtocol(Protocol):
    """The repository surface AnalysisService depends on (fake-able)."""

    def add(self, analysis: Analysis) -> Analysis: ...

    def list_for_user(self, user_id: UUID) -> list[Analysis]: ...

    def get_for_user(self, analysis_id: UUID, user_id: UUID) -> Analysis | None: ...

    def get_with_results(self, analysis_id: UUID, user_id: UUID) -> Analysis | None: ...

    def delete(self, analysis: Analysis) -> None: ...
    def flush(self) -> None: ...
    def commit(self) -> None: ...

class AnalysisService:
    """Application logic for analyses, always scoped to a user."""

    def __init__(self, repository: AnalysisRepositoryProtocol) -> None:
        self._repository = repository

    def create(self, user_id: UUID, payload: AnalysisCreate) -> Analysis:
        analysis = Analysis(
            user_id=user_id,
            type=payload.type,
            input_payload=payload.input_payload.model_dump(mode="json", exclude_none=True),
            status=AnalysisStatus.PENDING,
        )
        self._repository.add(analysis)
        self._repository.flush()
        self._repository.commit()
        return analysis



    def list_for_user(self, user_id: UUID) -> list[Analysis]:
        return self._repository.list_for_user(user_id)

    def get_for_user(self, analysis_id: UUID, user_id: UUID) -> Analysis:
        analysis = self._repository.get_for_user(analysis_id, user_id)
        if analysis is None:
            raise NotFoundError("Analysis not found")
        return analysis

    def get_with_results(self, analysis_id: UUID, user_id: UUID) -> Analysis:
        analysis = self._repository.get_with_results(analysis_id, user_id)
        if analysis is None:
            raise NotFoundError("Analysis not found")
        return analysis

    def delete_for_user(self, analysis_id: UUID, user_id: UUID) -> None:
        self._repository.delete(self.get_for_user(analysis_id, user_id))
