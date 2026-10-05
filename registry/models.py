"""Pydantic v2 models for the first robot knowledge registry."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Identifier = Annotated[
    str,
    Field(
        min_length=2,
        max_length=64,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Stable, lowercase, hyphenated identifier.",
    ),
]
GpuArchitecture = Literal["turing", "ampere", "ada", "blackwell"]


class RegistryModel(BaseModel):
    """Base configuration shared by all persisted registry records."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Hardware(RegistryModel):
    id: Identifier
    kind: Annotated[str, Field(min_length=1, max_length=64)]
    vendor: Annotated[str, Field(min_length=1, max_length=128)]
    capability_ids: list[Identifier] = Field(default_factory=list)


class Driver(RegistryModel):
    id: Identifier
    hardware_id: Identifier
    ros_distro: Annotated[str, Field(min_length=1, max_length=32)]


class RosInterface(RegistryModel):
    id: Identifier
    topic: Annotated[str, Field(min_length=2, pattern=r"^/")]
    message_type: Annotated[str, Field(min_length=3)]


class Capability(RegistryModel):
    id: Identifier
    interface_ids: list[Identifier] = Field(default_factory=list)
    template_id: Identifier | None = None


class Package(RegistryModel):
    id: Identifier
    required_capability_ids: list[Identifier] = Field(default_factory=list)
    required_interface_ids: list[Identifier] = Field(default_factory=list)
    minimum_gpu_architecture: GpuArchitecture | None = None


class Compatibility(RegistryModel):
    hardware_id: Identifier
    package_id: Identifier
    status: Annotated[str, Field(pattern=r"^(validated|experimental|blocked)$")]
    target_platforms: list[Literal["ubuntu-x86-64", "jetson"]] = Field(
        default_factory=list
    )
    note: str | None = None


class Conversion(RegistryModel):
    id: Identifier
    source_interface_id: Identifier
    target_interface_id: Identifier
    package_id: Identifier


class RobotKnowledgeRegistry(RegistryModel):
    """A self-consistent, serializable registry of robot integration facts."""

    hardware: list[Hardware] = Field(default_factory=list)
    drivers: list[Driver] = Field(default_factory=list)
    interfaces: list[RosInterface] = Field(default_factory=list)
    capabilities: list[Capability] = Field(default_factory=list)
    packages: list[Package] = Field(default_factory=list)
    compatibility: list[Compatibility] = Field(default_factory=list)
    conversions: list[Conversion] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> RobotKnowledgeRegistry:
        hardware_ids = _ids(self.hardware)
        capability_ids = _ids(self.capabilities)
        interface_ids = _ids(self.interfaces)
        package_ids = _ids(self.packages)
        _ids(self.conversions)

        _require_references(
            (driver.hardware_id for driver in self.drivers),
            hardware_ids,
            "driver references unknown hardware",
        )
        _require_references(
            (
                capability_id
                for hardware in self.hardware
                for capability_id in hardware.capability_ids
            ),
            capability_ids,
            "hardware references unknown capability",
        )
        _require_references(
            (
                interface_id
                for capability in self.capabilities
                for interface_id in capability.interface_ids
            ),
            interface_ids,
            "capability references unknown interface",
        )
        _require_references(
            (
                capability_id
                for package in self.packages
                for capability_id in package.required_capability_ids
            ),
            capability_ids,
            "package requires unknown capability",
        )
        _require_references(
            (
                interface_id
                for package in self.packages
                for interface_id in package.required_interface_ids
            ),
            interface_ids,
            "package requires unknown interface",
        )
        _require_references(
            (entry.hardware_id for entry in self.compatibility),
            hardware_ids,
            "compatibility references unknown hardware",
        )
        _require_references(
            (entry.package_id for entry in self.compatibility),
            package_ids,
            "compatibility references unknown package",
        )
        _require_references(
            (conversion.source_interface_id for conversion in self.conversions),
            interface_ids,
            "conversion references unknown source interface",
        )
        _require_references(
            (conversion.target_interface_id for conversion in self.conversions),
            interface_ids,
            "conversion references unknown target interface",
        )
        _require_references(
            (conversion.package_id for conversion in self.conversions),
            package_ids,
            "conversion references unknown package",
        )
        return self


def _ids(records: list[RegistryModel]) -> set[str]:
    identifiers = [record.id for record in records]  # type: ignore[attr-defined]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("registry contains duplicate identifiers")
    return set(identifiers)


def _require_references(
    references: object,
    available_ids: set[str],
    error: str,
) -> None:
    missing = sorted(set(references) - available_ids)  # type: ignore[arg-type]
    if missing:
        raise ValueError(f"{error}: {', '.join(missing)}")
