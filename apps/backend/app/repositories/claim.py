"""Repository for the Claim model."""

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.repository import Repository
from app.models.claim import Claim


class ClaimRepository(Repository[Claim]):
    """CRUD for claims."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Claim)

    def delete_for_analysis(self, analysis_id: UUID) -> None:
        self._session.execute(delete(Claim).where(Claim.analysis_id == analysis_id))
