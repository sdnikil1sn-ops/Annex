"""Repository for the Analysis model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.repository import Repository
from app.models.analysis import Analysis
from app.models.claim import Claim


class AnalysisRepository(Repository[Analysis]):
    """CRUD plus ownership-scoped queries for analyses."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Analysis)

    def list_for_user(self, user_id: UUID) -> list[Analysis]:
        stmt = (
            select(Analysis)
            .options(selectinload(Analysis.claims))
            .where(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
        )
        return list(self._session.scalars(stmt).all())

    def get_for_user(self, analysis_id: UUID, user_id: UUID) -> Analysis | None:
        stmt = select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == user_id,
        )
        return self._session.scalars(stmt).first()

    def get_with_results(self, analysis_id: UUID, user_id: UUID) -> Analysis | None:
        """Load an analysis with its claims, sources, and evidence eagerly."""
        stmt = (
            select(Analysis)
            .options(
                selectinload(Analysis.claims).selectinload(Claim.sources),
                selectinload(Analysis.claims).selectinload(Claim.evidence),
            )
            .where(
                Analysis.id == analysis_id,
                Analysis.user_id == user_id,
            )
        )
        return self._session.scalars(stmt).first()
