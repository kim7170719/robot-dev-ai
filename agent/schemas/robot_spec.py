"""Validated, template-ready description of a requested robot."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Provenance = Literal["user", "inferred", "default"]
MvpCapabilityId = Literal[
    "differential-drive",
    "planar-lidar",
    "rgb-camera",
    "navigation",
    "gpu-image-resize",
]


class RobotSpecification(BaseModel):
    """The deterministic input to registry and template selection."""

    model_config = ConfigDict(extra="forbid")

    capability_ids: list[MvpCapabilityId] = Field(default_factory=list)
    simulator: Literal["isaac-sim"] | None = None


class RequirementResult(BaseModel):
    """A parsed specification with its unresolved questions and origins."""

    model_config = ConfigDict(extra="forbid")

    specification: RobotSpecification
    ambiguities: list[str] = Field(default_factory=list)
    provenance: dict[str, Provenance] = Field(default_factory=dict)
