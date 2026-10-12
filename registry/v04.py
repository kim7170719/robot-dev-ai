"""Versioned v0.4 integration-schema records and v0.3 registry migration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import Field

from .models import Identifier, RegistryModel, RobotKnowledgeRegistry


SchemaVersion = Literal["v0.3", "v0.4"]
VerificationState = Literal["verified", "experimental", "unknown"]
ArchitectureClass = Literal[
    "linux-onboard",
    "host-plus-mcu",
    "remote-host-plus-mcu",
    "mcu-only",
    "distributed-edge",
    "simulator-only",
]
EvidenceStatus = Literal[
    "pass",
    "fail",
    "blocked",
    "not-tested",
    "unsupported",
    "degraded",
]


class ResourceProfile(RegistryModel):
    """Declared compute constraints used by a later architecture resolver."""

    id: Identifier
    cpu_arch: Annotated[str, Field(min_length=1, max_length=64)]
    ram_gb: Annotated[float, Field(ge=0)]
    storage_gb: Annotated[float, Field(ge=0)]
    gpu: str | None = None
    vram_gb: Annotated[float | None, Field(ge=0)] = None
    cuda: str | None = None
    power_budget_w: Annotated[float | None, Field(gt=0)] = None


class HardwareProfileV04(RegistryModel):
    """Capability and evidence state for one physical or simulated device."""

    device_id: Identifier
    device_class: Annotated[str, Field(min_length=1, max_length=64)]
    capability_ids: list[Identifier] = Field(default_factory=list)
    transport_ids: list[Identifier] = Field(default_factory=list)
    verification_state: VerificationState
    limitations: list[Annotated[str, Field(min_length=1)]] = Field(default_factory=list)
    provenance: Annotated[str, Field(min_length=1, max_length=128)]


class RobotSpecV04(RegistryModel):
    """Architecture-aware request shape; resolver behavior is introduced later."""

    robot_type: Identifier
    capability_ids: list[Identifier] = Field(default_factory=list)
    requested_architecture: ArchitectureClass | Literal["auto"] = "auto"
    device_ids: list[Identifier] = Field(default_factory=list)


class ArchitectureAssignment(RegistryModel):
    """One declared responsibility allocation in an architecture plan."""

    device_id: Identifier
    responsibility_ids: list[Identifier] = Field(default_factory=list)


class ArchitecturePlan(RegistryModel):
    """A resolver-owned topology plan, separate from artifact generation."""

    architecture: ArchitectureClass
    assignments: list[ArchitectureAssignment] = Field(default_factory=list)
    evidence_status: EvidenceStatus = "not-tested"


class CompositionComponent(RegistryModel):
    """A deterministic template or adapter selection in a composition plan."""

    kind: Literal["template", "adapter"]
    id: Identifier
    device_id: Identifier | None = None


class CompositionPlan(RegistryModel):
    """Ordered component selections before rendering any files."""

    components: list[CompositionComponent] = Field(default_factory=list)
    evidence_status: EvidenceStatus = "not-tested"


class RegistryDocumentV04(RegistryModel):
    """v0.4 registry envelope retaining validated v0.3 facts during migration."""

    schema_version: Literal["v0.4"] = "v0.4"
    source_schema_version: Literal["v0.3"]
    registry: RobotKnowledgeRegistry
    hardware_profiles: list[HardwareProfileV04] = Field(default_factory=list)
    resource_profiles: list[ResourceProfile] = Field(default_factory=list)


def migrate_v03_registry(
    payload: Mapping[str, Any] | RobotKnowledgeRegistry,
) -> RegistryDocumentV04:
    """Wrap validated v0.3 facts without inventing unsupported verification."""
    registry = (
        payload
        if isinstance(payload, RobotKnowledgeRegistry)
        else RobotKnowledgeRegistry.model_validate(payload)
    )
    return RegistryDocumentV04(
        source_schema_version="v0.3",
        registry=registry,
        hardware_profiles=[
            HardwareProfileV04(
                device_id=hardware.id,
                device_class=hardware.kind,
                capability_ids=hardware.capability_ids,
                verification_state="unknown",
                provenance="migrated-v0.3",
            )
            for hardware in registry.hardware
        ],
    )
