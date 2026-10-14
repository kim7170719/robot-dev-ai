"""G14.5 component-library artifacts and a dependency-free seed-manifest loader."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .models import Identifier, RegistryModel
from .v04 import EvidenceStatus
from .v05 import SourceType, TrustLevel


ArtifactType = Literal[
    "hardware_profile",
    "software_package",
    "driver_sdk",
    "protocol",
    "adapter",
    "component_template",
    "simulation_adapter",
    "validation_recipe",
    "evidence_record",
]
EvidenceLevel = Literal["E0", "E1", "E2", "E3", "E4", "E5"]


class ArtifactLicense(RegistryModel):
    """Declared source-license metadata, including an explicit unknown state."""

    spdx: str = Field(min_length=1, max_length=128)
    redistribution: Literal["allowed", "prohibited", "unknown"]


class ArtifactSource(RegistryModel):
    """Traceable metadata source; loading it never fetches the URL."""

    source_type: SourceType
    url: str = Field(min_length=8, max_length=2048, pattern=r"^https?://")
    trust_level: TrustLevel
    license: ArtifactLicense
    retrieved_at: date
    source_commit: str | None = Field(default=None, min_length=1, max_length=128)


class ArtifactConstraints(RegistryModel):
    """Declared compatibility envelope; empty lists mean no claim was recorded."""

    os: list[str] = Field(default_factory=list)
    ros_distro: list[str] = Field(default_factory=list)
    cpu_arch: list[str] = Field(default_factory=list)
    firmware: list[str] = Field(default_factory=list)
    runtime: list[str] = Field(default_factory=list)


class ArtifactVerification(RegistryModel):
    """Current evidence observation and the highest intended next gate."""

    evidence_level: EvidenceLevel
    status: EvidenceStatus
    target_evidence_level: EvidenceLevel

    @model_validator(mode="after")
    def reject_unavailable_real_or_community_claims(self) -> ArtifactVerification:
        if self.evidence_level in {"E4", "E5"}:
            raise ValueError("G14.5 seed artifacts cannot claim E4 or E5 evidence")
        return self


class ComponentArtifact(RegistryModel):
    """One narrow component record linked later to the frozen core registry."""

    id: Identifier
    name: str = Field(min_length=1, max_length=128)
    artifact_type: ArtifactType
    vendor: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    version: str | None = Field(default=None, max_length=128)
    source: ArtifactSource
    capabilities: list[Identifier] = Field(default_factory=list)
    interfaces: list[Identifier] = Field(default_factory=list)
    transports: list[Identifier] = Field(default_factory=list)
    requires: list[Identifier] = Field(default_factory=list)
    constraints: ArtifactConstraints = Field(default_factory=ArtifactConstraints)
    limitations: list[str] = Field(default_factory=list)
    verification: ArtifactVerification
    provenance: str = Field(min_length=1, max_length=128)
    registry_version: Literal["g14.5"] = "g14.5"


class SeedManifest(RegistryModel):
    """Minimal G14.5 catalog; intentionally separate from legacy registry envelopes."""

    schema_version: Literal["g14.5"] = "g14.5"
    artifacts: list[ComponentArtifact] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_artifact_ids(self) -> SeedManifest:
        artifact_ids = [artifact.id for artifact in self.artifacts]
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("G14.5 seed manifest contains duplicate artifact identifiers")
        return self


def load_seed_manifest(path: Path) -> SeedManifest:
    """Load JSON-compatible YAML without installing a parser or fetching data."""
    return SeedManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
