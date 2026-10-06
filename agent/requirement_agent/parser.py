"""Deterministic baseline parser for explicit robot requirements."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from agent.schemas import RequirementResult, RobotSpecification

from .provider import StructuredOutputProvider


class RequirementAgent:
    """Extract explicitly stated MVP capabilities from a requirement."""

    def __init__(self, provider: StructuredOutputProvider | None = None) -> None:
        self._provider = provider

    def parse(self, natural_language: str) -> RequirementResult:
        if self._provider is not None:
            last_error: ValidationError | None = None
            for _ in range(2):
                output: dict[str, Any] = self._provider.complete(
                    natural_language,
                    RequirementResult.model_json_schema(),
                )
                try:
                    return RequirementResult.model_validate(output)
                except ValidationError as error:
                    last_error = error
            raise ValueError("provider returned invalid structured output twice") from last_error

        normalized = natural_language.casefold()
        capabilities: list[str] = []

        if "差速" in normalized or "differential-drive" in normalized:
            capabilities.append("differential-drive")
        if (
            "2d lidar" in normalized
            or "2d 雷達" in normalized
            or "lidar" in normalized
            or "雷達" in normalized
        ):
            capabilities.append("planar-lidar")
        if "rgb" in normalized or "camera" in normalized or "相機" in normalized:
            capabilities.append("rgb-camera")
        if (
            "nav2" in normalized
            or "navigation" in normalized
            or "自主導航" in normalized
        ):
            capabilities.append("navigation")

        simulator = "isaac-sim" if "isaac sim" in normalized else None
        provenance = {}
        if capabilities:
            provenance["capability_ids"] = "user"
        if simulator is not None:
            provenance["simulator"] = "user"
        ambiguities = []
        if not capabilities:
            ambiguities.append(
                "Specify at least one supported base, sensor, or navigation capability."
            )

        return RequirementResult(
            specification=RobotSpecification(
                capability_ids=capabilities,
                simulator=simulator,
            ),
            ambiguities=ambiguities,
            provenance=provenance,
        )
