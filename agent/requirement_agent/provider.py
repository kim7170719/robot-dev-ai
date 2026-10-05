"""Provider boundary for structured LLM output."""

from __future__ import annotations

from typing import Any, Protocol


class StructuredOutputProvider(Protocol):
    """Return JSON-compatible output constrained by a supplied schema."""

    def complete(
        self, natural_language: str, response_schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Produce one structured response for the supplied requirement."""
