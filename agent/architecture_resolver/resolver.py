"""Rule-based topology selection for v0.4 robot integration requests."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier
from registry.v04 import (
    ArchitectureClass,
    ArchitecturePlan,
    HardwareProfileV04,
    RobotSpecV04,
)


NAVIGATION_CAPABILITIES = {"navigation", "nav2-runtime"}
MCU_RESPONSIBILITIES = ("motor-control", "encoder-feedback", "real-time-loop")
LINUX_DEVICE_CLASSES = {"edge-compute", "linux-host", "host", "jetson"}
MCU_DEVICE_CLASSES = {"mcu", "microcontroller"}


class ArchitectureResolutionRequest(BaseModel):
    """Facts required to choose a topology without generating an artifact."""

    model_config = ConfigDict(extra="forbid")

    specification: RobotSpecV04
    hardware_profiles: list[HardwareProfileV04] = Field(default_factory=list)


class ArchitectureResolutionResult(BaseModel):
    """A deterministic architecture plan or explicit, non-executable conflict."""

    model_config = ConfigDict(extra="forbid")

    compatible: bool
    status: Literal["resolved", "architecture-conflict"]
    plan: ArchitecturePlan | None = None
    issues: list[str] = Field(default_factory=list)


class ArchitectureResolver:
    """Select a Linux/MCU topology from declared, not inferred, hardware facts."""

    def resolve(
        self, request: ArchitectureResolutionRequest
    ) -> ArchitectureResolutionResult:
        selected, missing = _selected_profiles(request)
        if missing:
            return _blocked(
                "robot specification references unknown device: " + ", ".join(missing)
            )

        host = next(
            (
                profile
                for profile in selected
                if profile.device_class in LINUX_DEVICE_CLASSES
                and "ros2-runtime" in profile.capability_ids
            ),
            None,
        )
        mcu = next(
            (
                profile
                for profile in selected
                if profile.device_class in MCU_DEVICE_CLASSES
            ),
            None,
        )
        requested_capabilities = set(request.specification.capability_ids)
        needs_navigation = bool(requested_capabilities & NAVIGATION_CAPABILITIES)
        mcu_responsibilities = [
            capability_id
            for capability_id in MCU_RESPONSIBILITIES
            if mcu is not None
            and capability_id in requested_capabilities
            and capability_id in mcu.capability_ids
        ]

        requested_architecture = request.specification.requested_architecture
        if requested_architecture == "mcu-only":
            if needs_navigation:
                return _blocked(
                    "architecture conflict: navigation requires a Linux host with "
                    "ros2-runtime"
                )
            if mcu is None:
                return _blocked(
                    "architecture conflict: requested mcu-only has no MCU profile"
                )
            return _resolved_mcu(mcu, mcu_responsibilities)
        if requested_architecture == "simulator-only":
            return ArchitectureResolutionResult(
                compatible=True,
                status="resolved",
                plan=ArchitecturePlan(architecture="simulator-only"),
            )
        if requested_architecture in {
            "host-plus-mcu",
            "remote-host-plus-mcu",
            "distributed-edge",
        }:
            if host is None or mcu is None:
                return _blocked(
                    f"architecture conflict: requested {requested_architecture} "
                    "requires both a Linux host and an MCU profile"
                )
            if needs_navigation and "nav2-runtime" not in host.capability_ids:
                return _blocked(
                    f"architecture conflict: host {host.device_id} lacks nav2-runtime"
                )
            return _resolved_host_topology(
                host.device_id,
                mcu,
                mcu_responsibilities,
                architecture=requested_architecture,
                include_navigation=needs_navigation,
            )
        if requested_architecture == "linux-onboard":
            if host is None:
                return _blocked(
                    "architecture conflict: requested linux-onboard has no Linux host"
                )
            if needs_navigation and "nav2-runtime" not in host.capability_ids:
                return _blocked(
                    f"architecture conflict: host {host.device_id} lacks nav2-runtime"
                )
            return _resolved_host_topology(
                host.device_id,
                None,
                [],
                architecture="linux-onboard",
                include_navigation=needs_navigation,
            )

        if needs_navigation:
            if host is None:
                return _blocked(
                    "architecture conflict: navigation requires a Linux host with "
                    "ros2-runtime"
                )
            if "nav2-runtime" not in host.capability_ids:
                return _blocked(
                    f"architecture conflict: host {host.device_id} lacks nav2-runtime"
                )
            return _resolved_host_topology(
                host.device_id,
                mcu,
                mcu_responsibilities,
                include_navigation=True,
            )

        if host is not None and mcu is not None:
            return _resolved_host_topology(
                host.device_id,
                mcu,
                mcu_responsibilities,
                include_navigation=False,
            )
        if host is not None:
            return ArchitectureResolutionResult(
                compatible=True,
                status="resolved",
                plan=ArchitecturePlan(
                    architecture="linux-onboard",
                    assignments=[
                        {"device_id": host.device_id, "responsibility_ids": ["ros2-runtime"]}
                    ],
                ),
            )
        if mcu is not None:
            return _resolved_mcu(mcu, mcu_responsibilities)
        return _blocked("architecture conflict: no supported compute or MCU profile")


def _selected_profiles(
    request: ArchitectureResolutionRequest,
) -> tuple[list[HardwareProfileV04], list[str]]:
    profiles = {profile.device_id: profile for profile in request.hardware_profiles}
    requested_ids = request.specification.device_ids or sorted(profiles)
    missing = sorted(set(requested_ids) - set(profiles))
    return [profiles[device_id] for device_id in requested_ids if device_id in profiles], missing


def _resolved_host_topology(
    host_id: Identifier,
    mcu: HardwareProfileV04 | None,
    mcu_responsibilities: list[str],
    *,
    architecture: ArchitectureClass | None = None,
    include_navigation: bool,
) -> ArchitectureResolutionResult:
    host_responsibilities = ["ros2-runtime"]
    if include_navigation:
        host_responsibilities.append("nav2-runtime")
    assignments = [
        {"device_id": host_id, "responsibility_ids": host_responsibilities}
    ]
    if mcu is not None:
        assignments.append(
            {
                "device_id": mcu.device_id,
                "responsibility_ids": mcu_responsibilities,
            }
        )
    return ArchitectureResolutionResult(
        compatible=True,
        status="resolved",
        plan=ArchitecturePlan(
            architecture=architecture
            or ("host-plus-mcu" if mcu is not None else "linux-onboard"),
            assignments=assignments,
        ),
    )


def _resolved_mcu(
    mcu: HardwareProfileV04,
    mcu_responsibilities: list[str],
) -> ArchitectureResolutionResult:
    return ArchitectureResolutionResult(
        compatible=True,
        status="resolved",
        plan=ArchitecturePlan(
            architecture="mcu-only",
            assignments=[
                {
                    "device_id": mcu.device_id,
                    "responsibility_ids": mcu_responsibilities,
                }
            ],
        ),
    )


def _blocked(issue: str) -> ArchitectureResolutionResult:
    return ArchitectureResolutionResult(
        compatible=False,
        status="architecture-conflict",
        issues=[issue],
    )
