"""Compose known capabilities into a plan without rendering or writing files."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from registry.v04 import (
    ArchitecturePlan,
    CompositionComponent,
    CompositionPlan,
    RegistryDocumentV04,
    RobotSpecV04,
)


class CompositionPlanningRequest(BaseModel):
    """The resolved architecture and facts needed to assemble components."""

    model_config = ConfigDict(extra="forbid")

    specification: RobotSpecV04
    architecture: ArchitecturePlan
    registry: RegistryDocumentV04


class CompositionPlanningResult(BaseModel):
    """A stable component graph or explicit reasons it cannot be assembled."""

    model_config = ConfigDict(extra="forbid")

    ready: bool
    plan: CompositionPlan | None = None
    issues: list[str] = Field(default_factory=list)


class CompositionPlanner:
    """Map declared capabilities to registry-authorized component templates."""

    def plan(self, request: CompositionPlanningRequest) -> CompositionPlanningResult:
        capabilities = {
            capability.id: capability for capability in request.registry.registry.capabilities
        }
        components: list[CompositionComponent] = []
        issues: list[str] = []
        seen_capabilities: set[str] = set()

        for capability_id in request.specification.capability_ids:
            if capability_id in seen_capabilities:
                continue
            seen_capabilities.add(capability_id)
            capability = capabilities.get(capability_id)
            if capability is None:
                issues.append(f"composition references unknown capability: {capability_id}")
                continue
            if capability.template_id is None:
                issues.append(f"capability {capability_id} has no component template")
                continue
            profile = next(
                (
                    profile
                    for profile in request.registry.hardware_profiles
                    if capability_id in profile.capability_ids
                ),
                None,
            )
            if profile is None:
                issues.append(
                    f"capability {capability_id} has no hardware profile for composition"
                )
                continue
            components.append(
                CompositionComponent(
                    kind="template",
                    id=capability.template_id,
                    device_id=profile.device_id,
                )
            )

        if issues:
            return CompositionPlanningResult(ready=False, issues=issues)
        return CompositionPlanningResult(
            ready=True,
            plan=CompositionPlan(components=components),
        )
