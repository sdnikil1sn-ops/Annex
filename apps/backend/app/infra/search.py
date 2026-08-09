"""Web search abstraction backed by Exa."""

from dataclasses import dataclass
from typing import Protocol

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SourceCandidate:
    """A single search result: URL, title, and a text snippet."""

    url: str
    title: str
    text: str = ""


class SearchClient(Protocol):
    """Contract for finding candidate sources for a claim."""

    def find_sources(self, claim_text: str) -> list[SourceCandidate]:
        """Return candidate sources for the claim (empty list on failure)."""
        ...


class ExaSearchClient:
    """Real web search backed by Exa (synchronous)."""

    def __init__(self, api_key: str) -> None:
        from exa_py import Exa  # lazy import: tests without the SDK still import

        self._exa = Exa(api_key)

    def find_sources(self, claim_text: str) -> list[SourceCandidate]:
        try:
            results = self._exa.search_and_contents(
                claim_text,
                highlights=True,
                num_results=3,
            )
            candidates: list[SourceCandidate] = []
            for result in results.results:
                candidates.append(
                    SourceCandidate(
                        url=result.url,
                        title=result.title or "",
                        text=(result.highlights[0] if result.highlights else "") or "",
                    )
                )
            return candidates
        except Exception:
            logger.warning("exa_search_failed", claim_text=claim_text)
            return []


class LinkExtractionSearchClient:
    """Offline stub (kept for tests/fallback)."""

    def find_sources(self, claim_text: str) -> list[SourceCandidate]:
        return []
