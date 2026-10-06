"""Deterministic first slice of the M12 prompt-to-MVP path."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agent.auto_debug import AutoDebugAgent, BuildCommandCollector, DiagnosisResult
from agent.compatibility_resolver import (
    CompatibilityResolver,
    ResolutionRequest,
    ResolutionResult,
)
from agent.requirement_agent import RequirementAgent
from agent.schemas import RequirementResult
from agent.template_engine import ExpansionRequest, ExpansionResult, TemplateExpander
from registry.models import Identifier, RobotKnowledgeRegistry


class MvpPipelineResult(BaseModel):
    """The reviewable result of the pre-build MVP path."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ready-for-build", "build-succeeded", "blocked"]
    requirements: RequirementResult
    resolution: ResolutionResult | None = None
    templates: list[ExpansionResult] = Field(default_factory=list)
    generated_package_root: Path | None = None
    build_diagnosis: DiagnosisResult | None = None
    issues: list[str] = Field(default_factory=list)


class MvpPipeline:
    """Compose existing M8–M10 capabilities without writing to disk."""

    def __init__(
        self,
        registry: RobotKnowledgeRegistry,
        hardware_id: Identifier,
        template_root: Path,
        output_root: Path | None = None,
        build_collector: BuildCommandCollector | None = None,
    ) -> None:
        self._registry = registry
        self._hardware_id = hardware_id
        self._expander = TemplateExpander(template_root)
        self._output_root = output_root
        self._build_collector = build_collector

    def run(self, request: str) -> MvpPipelineResult:
        """Parse, resolve, and render the frozen differential-drive MVP plan."""

        requirements = RequirementAgent().parse(request)
        if requirements.ambiguities:
            return MvpPipelineResult(
                status="blocked",
                requirements=requirements,
                issues=requirements.ambiguities,
            )

        resolution = CompatibilityResolver().resolve(
            self._registry,
            ResolutionRequest(
                hardware_id=self._hardware_id,
                specification=requirements.specification,
                ros_distro="jazzy",
                target_platform="ubuntu-x86-64",
            ),
        )
        if not resolution.compatible:
            return MvpPipelineResult(
                status="blocked",
                requirements=requirements,
                resolution=resolution,
                issues=resolution.issues,
            )

        templates: list[ExpansionResult] = []
        try:
            for capability_id in requirements.specification.capability_ids:
                templates.append(
                    self._expander.expand(
                        self._registry,
                        ExpansionRequest(
                            hardware_id=self._hardware_id,
                            capability_id=capability_id,
                            values=_template_values(capability_id),
                        ),
                    )
                )
        except ValueError as error:
            return MvpPipelineResult(
                status="blocked",
                requirements=requirements,
                resolution=resolution,
                issues=[str(error)],
            )
        generated_package_root = None
        if self._output_root is not None:
            generated_package_root = self._output_root / "mvp_diff_drive"
            if generated_package_root.exists():
                return MvpPipelineResult(
                    status="blocked",
                    requirements=requirements,
                    resolution=resolution,
                    templates=templates,
                    issues=[
                        "refusing to overwrite existing generated package: "
                        f"{generated_package_root}"
                    ],
                )
            for template in templates:
                self._expander.write(template, generated_package_root)
        if self._build_collector is not None:
            if generated_package_root is None:
                return MvpPipelineResult(
                    status="blocked",
                    requirements=requirements,
                    resolution=resolution,
                    templates=templates,
                    issues=["build collection requires a generated package output root"],
                )
            build_diagnosis = AutoDebugAgent().diagnose(
                self._build_collector.collect(["mvp_diff_drive"])
            )
            if build_diagnosis.category != "build-succeeded":
                return MvpPipelineResult(
                    status="blocked",
                    requirements=requirements,
                    resolution=resolution,
                    templates=templates,
                    generated_package_root=generated_package_root,
                    build_diagnosis=build_diagnosis,
                    issues=[build_diagnosis.category],
                )
            return MvpPipelineResult(
                status="build-succeeded",
                requirements=requirements,
                resolution=resolution,
                templates=templates,
                generated_package_root=generated_package_root,
                build_diagnosis=build_diagnosis,
            )
        return MvpPipelineResult(
            status="ready-for-build",
            requirements=requirements,
            resolution=resolution,
            templates=templates,
            generated_package_root=generated_package_root,
        )


def _template_values(capability_id: str) -> dict[str, str]:
    """Return frozen MVP defaults for templates with declared placeholders."""

    if capability_id == "differential-drive":
        return {
            "package_name": "mvp_diff_drive",
            "base_frame": "base_link",
            "cmd_vel_topic": "/cmd_vel",
            "wheel_radius_m": "0.05",
            "wheel_separation_m": "0.30",
        }
    if capability_id == "navigation":
        return {
            "base_frame": "base_link",
            "odom_frame": "odom",
            "map_frame": "map",
            "odom_topic": "/odom",
        }
    if capability_id == "planar-lidar":
        return {
            "scan_topic": "/scan",
            "frame_id": "lidar_link",
        }
    if capability_id == "rgb-camera":
        return {
            "frame_id": "camera_link",
            "image_topic": "/camera/image_raw",
            "camera_info_topic": "/camera/camera_info",
        }
    return {}
