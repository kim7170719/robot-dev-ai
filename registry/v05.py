"""Trusted-source and lifecycle records for the v0.5 registry-management flow."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from .models import Identifier, RegistryModel
from .v04 import RegistryDocumentV04


SourceType = Literal[
    "official-repo", "ros-index", "vendor-sdk", "community-repo", "protocol-doc"
]
TrustLevel = Literal["A", "B", "C", "BLOCKED"]
ComponentKind = Literal[
    "hardware", "package", "driver", "firmware", "adapter", "template", "sdk", "protocol"
]
LifecycleState = Literal[
    "unknown",
    "discovered",
    "experimental",
    "tested",
    "verified",
    "deprecated",
    "blocked",
    "unsupported",
    "security-review-required",
]
ReviewDisposition = Literal["metadata-only", "sandbox-only", "blocked"]


class SourceLicense(RegistryModel):
    """License facts retained before an external artifact can be acquired."""

    spdx: str = Field(min_length=1, max_length=128)
    redistribution: Literal["allowed", "prohibited", "unknown"]


class CompatibilityClaim(RegistryModel):
    """A source claim, not a locally verified compatibility assertion."""

    ros_distros: list[str] = Field(default_factory=list)
    operating_systems: list[str] = Field(default_factory=list)
    cpu_architectures: list[str] = Field(default_factory=list)


class TrustedSource(RegistryModel):
    """Traceable source metadata. This model never fetches its URL."""

    id: Identifier
    source_type: SourceType
    url: str = Field(min_length=8, max_length=2048, pattern=r"^https?://")
    trust_level: TrustLevel
    license: SourceLicense
    vendor: str | None = Field(default=None, max_length=128)
    maintainer: str | None = Field(default=None, max_length=128)
    release: str | None = Field(default=None, max_length=128)
    commit: str | None = Field(default=None, max_length=128)
    retrieved_at: date
    compatibility_claim: CompatibilityClaim = Field(default_factory=CompatibilityClaim)


class ManagedComponent(RegistryModel):
    """A registry-management projection linked to a single traceable source."""

    id: Identifier
    kind: ComponentKind
    display_name: str = Field(min_length=1, max_length=128)
    source_id: Identifier
    lifecycle: LifecycleState
    version: str | None = Field(default=None, max_length=128)
    evidence_component_id: Identifier | None = None
    provenance: str = Field(min_length=1, max_length=128)


class SourceReview(RegistryModel):
    """A policy result that deliberately contains no fetch or execution action."""

    source_id: Identifier
    disposition: ReviewDisposition
    reasons: list[str] = Field(default_factory=list)


class RegistryManagementDocumentV05(RegistryModel):
    """v0.5 view over the frozen v0.4 registry and trusted source metadata."""

    schema_version: Literal["v0.5"] = "v0.5"
    source_schema_version: Literal["v0.4"]
    registry_v04: RegistryDocumentV04
    sources: list[TrustedSource] = Field(default_factory=list)
    components: list[ManagedComponent] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_management_references(self) -> RegistryManagementDocumentV05:
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("v0.5 registry contains duplicate trusted source identifiers")
        component_ids = [component.id for component in self.components]
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("v0.5 registry contains duplicate managed component identifiers")
        unknown = sorted({component.source_id for component in self.components} - set(source_ids))
        if unknown:
            raise ValueError("managed component references unknown source: " + ", ".join(unknown))
        return self
