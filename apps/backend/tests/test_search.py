"""Tests for the web search abstraction."""

import pytest

from app.infra.search import ExaSearchClient, SourceCandidate


def test_source_candidate_fields() -> None:
    candidate = SourceCandidate(
        url="https://example.com",
        title="Example",
        text="snippet",
    )
    assert candidate.url == "https://example.com"
    assert candidate.title == "Example"
    assert candidate.text == "snippet"


def test_exa_search_client_constructs() -> None:
    client = ExaSearchClient(api_key="dummy-key")
    assert client is not None


def test_exa_search_fails_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    client = ExaSearchClient(api_key="dummy-key")

    class _Boom:
        def search_and_contents(self, *args: object, **kwargs: object) -> object:
            raise RuntimeError("provider down")

    monkeypatch.setattr(client, "_exa", _Boom())
    assert client.find_sources("some claim") == []
