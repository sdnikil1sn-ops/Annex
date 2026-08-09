"""Analysis endpoints (authenticated, ownership-scoped)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_analysis_service
from app.core.config import get_settings
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisRead
from app.services.analysis import AnalysisService
from app.services.auth import get_current_user
from app.tasks import analysis as analysis_tasks

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _enqueue(analysis_id: str) -> None:
    """Dispatch the pipeline task (async if configured, else eager inline)."""
    if get_settings().analysis_run_async:
        analysis_tasks.run_analysis_pipeline.delay(analysis_id)
    else:
        analysis_tasks.run_analysis_pipeline.apply(args=[analysis_id])


@router.post("", response_model=AnalysisRead, status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisRead:
    """Create a new analysis (job starts as pending) and enqueue the pipeline."""
    analysis = service.create(current_user.id, payload)
    _enqueue(str(analysis.id))
    return analysis  # type: ignore[return-value]


@router.get("", response_model=list[AnalysisRead])
def list_analyses(
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> list[AnalysisRead]:
    """List the current user's analyses, newest first."""
    return service.list_for_user(current_user.id)  # type: ignore[return-value]


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisRead:
    """Get one analysis with its claims, sources, and evidence."""
    return service.get_with_results(analysis_id, current_user.id)  # type: ignore[return-value]


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> Response:
    """Delete one of the current user's analyses (cascades to claims/sources/evidence)."""
    service.delete_for_user(analysis_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
