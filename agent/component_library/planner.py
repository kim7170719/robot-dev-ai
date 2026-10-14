"""Produce a reviewable Reference Robot A plan from G14.5 seed artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agent.architecture_resolver import ArchitectureResolutionRequest, ArchitectureResolver
from agent.composition_planner import CompositionPlanner, CompositionPlanningRequest
from registry.g145 import SeedManifest, build_reference_registry
from registry.models import Identifier
from registry.v04 import ArchitecturePlan, CompositionPlan, RobotSpecV04


class ReferenceRobotSpec(BaseModel):
    """Declared Reference Robot A facts; this model has no hardware authority."""

    model_config = ConfigDict(extra="forbid")

    id: Identifier
    display_name: str = Field(min_length=1, max_length=128)
    robot_spec: RobotSpecV04
    adapter_ids: list[Identifier] = Field(default_factory=list)
    package_ids: list[Identifier] = Field(default_factory=list)
    driver_ids: list[Identifier] = Field(default_factory=list)


class ReferenceCompositionResult(BaseModel):
    """Deterministic G14.5 planning output, intentionally separate from deployment."""

    model_config = ConfigDict(extra="forbid")

    ready: bool
    architecture_plan: ArchitecturePlan | None = None
    composition_plan: CompositionPlan | None = None
    required_packages: list[Identifier] = Field(default_factory=list)
    required_drivers: list[Identifier] = Field(default_factory=list)
    required_adapters: list[Identifier] = Field(default_factory=list)
    missing_dependencies: list[Identifier] = Field(default_factory=list)
    evidence_gaps: list[Identifier] = Field(default_factory=list)
    hardware_readiness: Literal["blocked", "not-tested"] = "not-tested"
    deployment_checklist: list[str] = Field(default_factory=list)
    validation_plan: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class ComponentLibraryPlanner:
    """Connect the seed catalog to existing resolvers without rendering or I/O."""

    def plan(
        self, manifest: SeedManifest, specification: ReferenceRobotSpec
    ) -> ReferenceCompositionResult:
        artifact_ids = {artifact.id for artifact in manifest.artifacts}
        requested_ids = set(
            specification.robot_spec.device_ids
            + specification.adapter_ids
            + specification.package_ids
            + specification.driver_ids
        )
        missing = sorted(requested_ids - artifact_ids)
        if missing:
            return ReferenceCompositionResult(
                ready=False,
                missing_dependencies=missing,
                hardware_readiness="blocked",
                issues=["reference composition references unknown seed artifacts: " + ", ".join(missing)],
            )

        registry = build_reference_registry(manifest)
        architecture = ArchitectureResolver().resolve(
            ArchitectureResolutionRequest(
                specification=specification.robot_spec,
                hardware_profiles=registry.hardware_profiles,
            )
        )
        if not architecture.compatible or architecture.plan is None:
            return ReferenceCompositionResult(
                ready=False,
                hardware_readiness="blocked",
                issues=architecture.issues,
            )
        template_capabilities = {
            capability.id
            for capability in registry.registry.capabilities
            if capability.template_id is not None
        }
        composition_specification = specification.robot_spec.model_copy(
            update={
                "capability_ids": [
                    capability_id
                    for capability_id in specification.robot_spec.capability_ids
                    if capability_id in template_capabilities
                ]
            }
        )
        composition = CompositionPlanner().plan(
            CompositionPlanningRequest(
                specification=composition_specification,
                architecture=architecture.plan,
                registry=registry,
            )
        )
        if not composition.ready or composition.plan is None:
            return ReferenceCompositionResult(
                ready=False,
                architecture_plan=architecture.plan,
                hardware_readiness="blocked",
                issues=composition.issues,
            )

        required = set(
            specification.robot_spec.device_ids
            + specification.adapter_ids
            + specification.package_ids
            + specification.driver_ids
        )
        evidence_gaps = sorted(
            artifact.id
            for artifact in manifest.artifacts
            if artifact.id in required
            and artifact.verification.evidence_level != artifact.verification.target_evidence_level
        )
        return ReferenceCompositionResult(
            ready=True,
            architecture_plan=architecture.plan,
            composition_plan=composition.plan,
            required_packages=specification.package_ids,
            required_drivers=specification.driver_ids,
            required_adapters=specification.adapter_ids,
            evidence_gaps=evidence_gaps,
            hardware_readiness="blocked",
            deployment_checklist=[
                "record the actual Jetson, base, MCU, LiDAR, and D455 identities",
                "verify independent emergency-stop and safe power behavior",
                "record encoder, motor, LiDAR, and D455 interface observations",
                "run staged motion tests before autonomous navigation",
            ],
            validation_plan=[
                "review source metadata before any external acquisition",
                "run E2 only with an approved archive and local Jazzy sandbox image",
                "run the existing Isaac simulation validation before M15",
                "record M15 observations separately before any E4 promotion",
            ],
        )


def load_reference_robot_spec(path: Path) -> ReferenceRobotSpec:
    """Load a repository-owned JSON-compatible YAML spec without side effects."""
    return ReferenceRobotSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_default_reference_robot_spec() -> ReferenceRobotSpec:
    return load_reference_robot_spec(
        Path(__file__).parents[2] / "data" / "reference_robot_a" / "robot_spec.yaml"
    )
