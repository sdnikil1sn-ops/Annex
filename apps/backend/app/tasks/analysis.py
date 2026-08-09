"""Celery tasks for the analysis pipeline."""

import structlog
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.infra.celery_app import celery_app
from app.infra.llm import OpenAILLMClient
from app.infra.search import ExaSearchClient
from app.models.analysis import Analysis, AnalysisStatus
from app.models.notification import NotificationType
from app.repositories.notification import NotificationRepository
from app.services.analysis_pipeline import AnalysisPipelineService
from app.services.notification import NotificationService

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.analysis.run_analysis_pipeline")  # type: ignore[untyped-decorator]
def run_analysis_pipeline(analysis_id: str) -> None:
    """Run the full analysis pipeline (worker-side)."""
    settings = get_settings()
    session: Session = SessionLocal()
    try:
        # Claim: only a pending analysis may start processing.
        analysis = session.get(Analysis, analysis_id)
        if analysis is None:
            logger.info("analysis_not_found", analysis_id=analysis_id)
            return
        if analysis.status != AnalysisStatus.PENDING:
            logger.info("analysis_not_pending", analysis_id=analysis_id)
            return
        analysis.status = AnalysisStatus.PROCESSING
        session.commit()
        session.refresh(analysis)

        pipeline = AnalysisPipelineService(
            session=session,
            llm=OpenAILLMClient(
                settings.openai_api_key,
                settings.openai_model,
                settings.openai_base_url,
            ),
            search=ExaSearchClient(settings.exa_api_key),

        )
        pipeline.run(analysis)
        NotificationService(NotificationRepository(session)).create_notification(
            user_id=analysis.user_id,
            type=NotificationType.ANALYSIS_COMPLETED,
            title="Analysis completed",
            body=analysis.summary or "Your analysis has finished.",
        )
        

        session.commit()
    except Exception:
        logger.exception("analysis_pipeline_failed", analysis_id=analysis_id)
        session.rollback()
        analysis = session.get(Analysis, analysis_id)
        if analysis is not None:
            analysis.status = AnalysisStatus.FAILED
            analysis.error = "Analysis pipeline failed"
            session.commit()
    finally:
        session.close()
