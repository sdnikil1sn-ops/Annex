"""Analysis pipeline orchestration (pure logic, DI-friendly)."""

import structlog
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from app.infra.llm import LLMClient
from app.infra.search import SearchClient
from app.models.analysis import Analysis, AnalysisStatus, AnalysisType
from app.models.claim import Claim, ClaimStatus
from app.models.evidence import Evidence
from app.models.source import Source
from app.repositories.analysis import AnalysisRepository
from app.repositories.claim import ClaimRepository
from app.schemas.llm import LLMClaimExtraction, LLMVerification

logger = structlog.get_logger(__name__)

EXTRACTION_SYSTEM = (
    "You are a professional fact-checker. Extract the factual claims from the "
    'user input. Respond ONLY with JSON: {"claims": '
    '[{"claim_text": "string", "confidence": 0}]}. confidence is 0-100.'
)
VERIFICATION_SYSTEM = (
    "You are a professional fact-checker. Given a claim and candidate sources, "
    'respond ONLY with JSON: {"status": "verified|partially_verified|disputed|'
    'debunked", "summary": "string", "confidence": 0, "sources": '
    '[{"url": "string", "title": "string", "quote": "string"}]}.'
)

_claims_adapter = TypeAdapter(LLMClaimExtraction)
_verification_adapter = TypeAdapter(LLMVerification)


class AnalysisPipelineService:
    """Extracts, verifies, and persists claims for one analysis."""

    def __init__(self, session: Session, llm: LLMClient, search: SearchClient) -> None:
        self._session = session
        self._analyses = AnalysisRepository(session)
        self._claims = ClaimRepository(session)
        self._llm = llm
        self._search = search

    @retry(
        retry=retry_if_exception_type(ValidationError),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _extract(self, text: str) -> LLMClaimExtraction:
        return _claims_adapter.validate_json(self._llm.complete_json(EXTRACTION_SYSTEM, text))

    def _extract_image(self, image_url: str) -> LLMClaimExtraction:
        return _claims_adapter.validate_json(
            self._llm.complete_vision(
                EXTRACTION_SYSTEM,
                "Extract every claim from the text visible in this image, "
                "then return the required JSON.",
                image_url,
            )
        )

    def _verify(self, claim_text: str) -> LLMVerification:
        candidates = self._search.find_sources(claim_text)
        evidence_lines: list[str] = []
        for s in candidates:
            snippet = getattr(s, "text", "") or ""
            title = getattr(s, "title", "") or ""
            if snippet:
                evidence_lines.append(f"- {title} ({s.url}): {snippet[:300]}")
            else:
                evidence_lines.append(f"- {s.url}")
        evidence = "\n".join(evidence_lines) or "(none found)"
        prompt = f"CLAIM: {claim_text}\nSOURCES:\n{evidence}"
        return _verification_adapter.validate_json(
            self._llm.complete_json(VERIFICATION_SYSTEM, prompt)
        )

    def run(self, analysis: Analysis) -> None:
        if analysis.type is AnalysisType.IMAGE:
            self._run_image(analysis)
            return
        if analysis.type in (AnalysisType.VIDEO, AnalysisType.VOICE):
            analysis.summary = "Video/voice analysis is coming in a later phase."
            analysis.status = AnalysisStatus.COMPLETED
            return

        text = str((analysis.input_payload or {}).get("text", ""))
        extraction = self._extract(text)
        self._persist_claims(analysis, extraction)

    def _run_image(self, analysis: Analysis) -> None:
        payload = analysis.input_payload or {}
        image_url = str(payload.get("url") or payload.get("path") or "")
        if not image_url:
            raise ValueError("Image analysis requires 'url' or 'path' in input_payload")

        extraction = self._extract_image(image_url)
        self._persist_claims(analysis, extraction)

    def _persist_claims(self, analysis: Analysis, extraction: LLMClaimExtraction) -> None:
        # Idempotency: clear prior claims before re-extracting.
        self._claims.delete_for_analysis(analysis.id)

        scores: list[int] = []
        for index, item in enumerate(extraction.claims):
            verdict = self._verify(item.claim_text)
            claim = Claim(
                analysis_id=analysis.id,
                claim_text=item.claim_text,
                status=ClaimStatus(verdict.status),
                confidence=verdict.confidence,
                position=index,
            )
            self._claims.add(claim)
            self._session.flush()  # populate claim.id

            for source in verdict.sources:
                src = Source(claim_id=claim.id, url=source.url, title=source.title)
                self._session.add(src)
                self._session.flush()  # populate src.id

                if source.quote:
                    self._session.add(
                        Evidence(
                            claim_id=claim.id,
                            source_id=src.id,
                            quote=source.quote,
                            url=source.url,
                        )
                    )

            scores.append(verdict.confidence)

        analysis.credibility_score = (
            round(sum(scores) / len(scores)) if scores else None
        )
        analysis.summary = f"{len(extraction.claims)} claims extracted and verified."
        analysis.status = AnalysisStatus.COMPLETED
