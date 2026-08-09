"""Pydantic schemas for LLM structured outputs."""

from pydantic import BaseModel, Field


class LLMSource(BaseModel):
    """A source suggested by the LLM or search client."""

    url: str
    title: str | None = None
    quote: str | None = None


class LLMClaim(BaseModel):
    """A single extracted claim."""

    claim_text: str = Field(min_length=1, max_length=2000)
    confidence: int = Field(ge=0, le=100)


class LLMClaimExtraction(BaseModel):
    """Envelope returned by the extraction call."""

    claims: list[LLMClaim]


class LLMVerification(BaseModel):
    """Verdict for one claim."""

    status: str  # verified | partially_verified | disputed | debunked
    summary: str | None = None
    confidence: int = Field(ge=0, le=100)
    sources: list[LLMSource] = Field(default_factory=list)
