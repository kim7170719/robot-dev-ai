"""Versioned v0.4 integration-schema records and v0.3 registry migration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

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
ConstraintKind = Literal[
    "ros-distro",
    "os",
    "cpu-arch",
    "memory",
    "vram",
    "firmware",
    "driver",
    "transport",
    "power",
    "sensor-rate",
]


class Constraint(RegistryModel):
    """A traceable requirement or limit used in later compatibility decisions."""

    id: Identifier
    kind: ConstraintKind
    expected_value: Annotated[str, Field(min_length=1, max_length=256)]
    provenance: Annotated[str, Field(min_length=1, max_length=128)]


class SoftwareProfileV04(RegistryModel):
    """A driver, SDK, or runtime fact with verification and provenance."""

    id: Identifier
    kind: Literal["driver", "sdk", "runtime", "firmware-tool"]
    version: Annotated[str, Field(min_length=1, max_length=128)] | None = None
    verification_state: VerificationState
    provenance: Annotated[str, Field(min_length=1, max_length=128)]


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
    driver_ids: list[Identifier] = Field(default_factory=list)
    constraint_ids: list[Identifier] = Field(default_factory=list)
    firmware_required: bool = False
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
    software_profiles: list[SoftwareProfileV04] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    resource_profiles: list[ResourceProfile] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_v04_references(self) -> RegistryDocumentV04:
        hardware_ids = {hardware.id for hardware in self.registry.hardware}
        profile_ids = [profile.device_id for profile in self.hardware_profiles]
        if len(profile_ids) != len(set(profile_ids)):
            raise ValueError("v0.4 registry contains duplicate hardware profile identifiers")
        unknown_profiles = sorted(set(profile_ids) - hardware_ids)
        if unknown_profiles:
            raise ValueError(
                "hardware profile references unknown hardware: "
                + ", ".join(unknown_profiles)
            )

        software_ids = _unique_v04_ids(self.software_profiles, "software profile")
        constraints_by_id = {constraint.id: constraint for constraint in self.constraints}
        if len(constraints_by_id) != len(self.constraints):
            raise ValueError("v0.4 registry contains duplicate constraint identifiers")
        for profile in self.hardware_profiles:
            _require_v04_references(
                profile.driver_ids,
                software_ids,
                f"hardware profile {profile.device_id} references unknown driver",
            )
            _require_v04_references(
                profile.constraint_ids,
                set(constraints_by_id),
                f"hardware profile {profile.device_id} references unknown constraint",
            )
            _require_v04_references(
                profile.transport_ids,
                {
                    constraint.id
                    for constraint in self.constraints
                    if constraint.kind == "transport"
                },
                f"hardware profile {profile.device_id} references unknown transport",
            )
        return self


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
        software_profiles=[
            SoftwareProfileV04(
                id=driver.id,
                kind="driver",
                verification_state="unknown",
                provenance="migrated-v0.3",
            )
            for driver in registry.drivers
        ],
        hardware_profiles=[
            HardwareProfileV04(
                device_id=hardware.id,
                device_class=hardware.kind,
                capability_ids=hardware.capability_ids,
                driver_ids=[
                    driver.id
                    for driver in registry.drivers
                    if driver.hardware_id == hardware.id
                ],
                verification_state="unknown",
                provenance="migrated-v0.3",
            )
            for hardware in registry.hardware
        ],
    )


def _unique_v04_ids(records: list[RegistryModel], label: str) -> set[str]:
    identifiers = [record.id for record in records]  # type: ignore[attr-defined]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"v0.4 registry contains duplicate {label} identifiers")
    return set(identifiers)


def _require_v04_references(
    references: list[str], available_ids: set[str], error: str
) -> None:
    missing = sorted(set(references) - available_ids)
    if missing:
        raise ValueError(f"{error}: {', '.join(missing)}")
