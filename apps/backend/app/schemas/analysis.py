"""Analysis request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.analysis import AnalysisStatus, AnalysisType


class AnalysisInput(BaseModel):
    """Validated input payload for an analysis request."""

    text: str | None = Field(default=None, max_length=100_000)
    url: str | None = Field(default=None, max_length=2048)
    # Image/video/voice inputs arrive with the Phase 6 upload flow.
    path: str | None = None          # media: storage path
    content_type: str | None = None  # media: e.g. image/jpeg

class AnalysisCreate(BaseModel):
    """Request body for creating an analysis."""

    type: AnalysisType
    input_payload: AnalysisInput


class SourceRead(BaseModel):
    """A source cited by a claim."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    title: str | None = None
    domain: str | None = None
    credibility_score: int | None = None


class EvidenceRead(BaseModel):
    """An evidence snippet linking a claim to a source."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    quote: str
    url: str
    relevance: int | None = None


class ClaimRead(BaseModel):
    """A claim with its sources and evidence."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    claim_text: str
    status: str
    confidence: int | None = None
    position: int = 0
    sources: list[SourceRead] = Field(default_factory=list)
    evidence: list[EvidenceRead] = Field(default_factory=list)


class AnalysisRead(BaseModel):
    """API representation of an analysis."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: AnalysisType
    status: AnalysisStatus
    input_payload: dict[str, object]
    summary: str | None = None
    credibility_score: int | None = None
    created_at: datetime
    claims: list[ClaimRead] = Field(default_factory=list)
