"""LLM client protocol + OpenAI implementation, with free-tier fallback."""

from typing import Protocol

import openai
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_FALLBACK_ERRORS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
)


class LLMClient(Protocol):
    """Minimal LLM surface used by the analysis pipeline."""

    def complete_json(self, system: str, user: str) -> str: ...
    def complete_vision(self, system: str, user: str, image_url: str) -> str:
        """Ask the model to inspect an image and return JSON."""
        ...


class OpenAILLMClient:
    """OpenAI-compatible chat completions with JSON mode and Groq fallback."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

        settings = get_settings()
        # Build the Groq fallback only for the primary client (never for itself).
        self._fallback: OpenAILLMClient | None = None
        self._fallback_vision: OpenAILLMClient | None = None
        if settings.groq_api_key and (not base_url or "groq" not in base_url.lower()):
            self._fallback = OpenAILLMClient(
                settings.groq_api_key,
                settings.groq_model,
                _GROQ_BASE_URL,
            )
            if settings.groq_vision_model:
                self._fallback_vision = OpenAILLMClient(
                    settings.groq_api_key,
                    settings.groq_vision_model,
                    _GROQ_BASE_URL,
                )

    def complete_json(self, system: str, user: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            return response.choices[0].message.content or "{}"
        except _FALLBACK_ERRORS:
            if self._fallback is not None:
                logger.warning("llm_fallback_triggered", method="complete_json")
                return self._fallback.complete_json(system, user)
            raise

    def complete_vision(self, system: str, user: str, image_url: str) -> str:
        """Ask the model to inspect an image and return JSON."""
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            return response.choices[0].message.content or "{}"
        except _FALLBACK_ERRORS:
            if self._fallback_vision is not None:
                logger.warning("llm_fallback_triggered", method="complete_vision")
                return self._fallback_vision.complete_vision(system, user, image_url)
            raise
