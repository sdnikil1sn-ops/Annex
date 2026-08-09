"""LLM client protocol + OpenAI implementation."""

from typing import Protocol

import openai


class LLMClient(Protocol):
    """Minimal LLM surface used by the analysis pipeline."""

    def complete_json(self, system: str, user: str) -> str: ...
    def complete_vision(self, system: str, user: str, image_url: str) -> str:
        """Ask the model to inspect an image and return JSON."""
        ...


class OpenAILLMClient:
    """OpenAI-compatible chat completions with JSON mode."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def complete_json(self, system: str, user: str) -> str:
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
    
    def complete_vision(self, system: str, user: str, image_url: str) -> str:
        """Ask the model to inspect an image and return JSON."""
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

