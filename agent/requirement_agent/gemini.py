"""Gemini implementation of the structured-output provider contract."""

from __future__ import annotations

import json
from typing import Any


class GeminiStructuredOutputProvider:
    """Request schema-constrained JSON from the Gemini Developer API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash-lite",
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._client = client or self._create_client(api_key)

    @staticmethod
    def _create_client(api_key: str) -> Any:
        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError(
                "Gemini support requires installing robot-dev-ai[gemini]"
            ) from error
        return genai.Client(api_key=api_key)

    def complete(
        self, natural_language: str, response_schema: dict[str, Any]
    ) -> dict[str, Any]:
        interaction = self._client.interactions.create(
            model=self._model,
            input=natural_language,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": response_schema,
            },
        )
        return json.loads(interaction.output_text)
