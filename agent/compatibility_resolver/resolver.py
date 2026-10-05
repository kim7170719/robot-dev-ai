"""Rule-based compatibility resolution over the robot knowledge registry."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agent.schemas import RobotSpecification
from registry.models import GpuArchitecture, Identifier, RobotKnowledgeRegistry


GPU_ARCHITECTURE_ORDER = {
    "turing": 0,
    "ampere": 1,
    "ada": 2,
    "blackwell": 3,
}


class ResolutionRequest(BaseModel):
    """The declared deployment context for a robot specification."""

    model_config = ConfigDict(extra="forbid")

    hardware_id: Identifier
    specification: RobotSpecification
    ros_distro: Literal["jazzy"]
    target_platform: Literal["ubuntu-x86-64", "jetson"]
    gpu_architecture: GpuArchitecture | None = None


class ResolutionResult(BaseModel):
    """The selected packages and rule-derived incompatibilities."""

    model_config = ConfigDict(extra="forbid")

    compatible: bool
    status: Literal["validated", "experimental", "blocked"]
    package_ids: list[Identifier] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CompatibilityResolver:
    """Select only registry-validated packages for a declared robot."""

    def resolve(
        self,
        registry: RobotKnowledgeRegistry,
        request: ResolutionRequest,
    ) -> ResolutionResult:
        issues: list[str] = []
        warnings: list[str] = []
        hardware = next(
            (item for item in registry.hardware if item.id == request.hardware_id),
            None,
        )
        if hardware is None:
            return ResolutionResult(
                compatible=False,
                status="blocked",
                issues=[f"unknown hardware: {request.hardware_id}"],
            )

        missing_capabilities = sorted(
            set(request.specification.capability_ids) - set(hardware.capability_ids)
        )
        if missing_capabilities:
            issues.append(
                "hardware lacks required capabilities: "
                + ", ".join(missing_capabilities)
            )

        if not any(
            driver.hardware_id == hardware.id and driver.ros_distro == request.ros_distro
            for driver in registry.drivers
        ):
            issues.append(
                f"hardware {hardware.id} has no driver for ROS {request.ros_distro}"
            )

        capability_interfaces = {
            interface_id
            for capability in registry.capabilities
            if capability.id in request.specification.capability_ids
            for interface_id in capability.interface_ids
        }
        for capability_id in request.specification.capability_ids:
            if (
                capability_id in hardware.capability_ids
                and not any(
                capability_id in package.required_capability_ids
                for package in registry.packages
                )
            ):
                issues.append(f"no package declares capability: {capability_id}")
        package_ids = []
        for package in registry.packages:
            if not (
                package.required_capability_ids or package.required_interface_ids
            ):
                continue
            if not set(package.required_capability_ids).issubset(
                request.specification.capability_ids
            ):
                continue
            all_entries = [
                entry
                for entry in registry.compatibility
                if (
                entry.hardware_id == hardware.id
                and entry.package_id == package.id
                )
            ]
            entries = [
                entry
                for entry in all_entries
                if entry.status in {"validated", "experimental"}
            ]
            if not entries:
                if any(entry.status == "blocked" for entry in all_entries):
                    issues.append(f"package {package.id} is blocked by registry")
                continue
            if any(
                entry.target_platforms
                and request.target_platform not in entry.target_platforms
                for entry in entries
            ):
                issues.append(
                    f"package {package.id} is unsupported on {request.target_platform}"
                )
                continue
            is_experimental = any(
                entry.status == "experimental" for entry in entries
            )
            gpu_warning_added = False
            if package.minimum_gpu_architecture is not None:
                if request.gpu_architecture is None:
                    issues.append(
                        f"package {package.id} requires GPU architecture "
                        f"{package.minimum_gpu_architecture}"
                    )
                    continue
                if (
                    GPU_ARCHITECTURE_ORDER[request.gpu_architecture]
                    < GPU_ARCHITECTURE_ORDER[package.minimum_gpu_architecture]
                ):
                    if is_experimental:
                        warnings.append(
                            f"package {package.id} requires "
                            f"{package.minimum_gpu_architecture.capitalize()}+; "
                            f"{request.gpu_architecture.capitalize()} is experimental"
                        )
                        gpu_warning_added = True
                    else:
                        issues.append(
                            f"package {package.id} requires "
                            f"{package.minimum_gpu_architecture.capitalize()}+"
                        )
                        continue
            if is_experimental and not gpu_warning_added:
                note = next(
                    (entry.note for entry in entries if entry.status == "experimental"),
                    None,
                )
                warning = f"package {package.id} is experimental"
                if note:
                    warning += f": {note}"
                warnings.append(warning)
            conversion_package_ids = []
            for interface_id in package.required_interface_ids:
                if interface_id in capability_interfaces:
                    continue
                conversion = next(
                    (
                        conversion
                        for conversion in registry.conversions
                        if conversion.source_interface_id == interface_id
                        and conversion.target_interface_id in capability_interfaces
                        and any(
                            entry.hardware_id == hardware.id
                            and entry.package_id == conversion.package_id
                            and entry.status == "validated"
                            and (
                                not entry.target_platforms
                                or request.target_platform in entry.target_platforms
                            )
                            for entry in registry.compatibility
                        )
                    ),
                    None,
                )
                if conversion is None:
                    issues.append(
                        f"package {package.id} requires unsupported interface: "
                        f"{interface_id}"
                    )
                    break
                conversion_package_ids.append(conversion.package_id)
            else:
                package_ids.append(package.id)
                for conversion_package_id in conversion_package_ids:
                    if conversion_package_id not in package_ids:
                        package_ids.append(conversion_package_id)
        status: Literal["validated", "experimental", "blocked"]
        if issues:
            status = "blocked"
        elif warnings:
            status = "experimental"
        else:
            status = "validated"
        return ResolutionResult(
            compatible=status != "blocked",
            status=status,
            package_ids=package_ids,
            issues=issues,
            warnings=warnings,
        )
