import json
from pathlib import Path

import pytest

from agent.architecture_resolver import ArchitectureResolutionRequest, ArchitectureResolver
from agent.composition_planner import CompositionPlanner, CompositionPlanningRequest
from agent.component_library import ComponentLibraryPlanner, ReferenceRobotSpec
from registry.g145 import (
    SeedManifest,
    build_reference_registry,
    load_default_seed_manifest,
    load_seed_manifest,
)
from registry.v04 import ArchitecturePlan, RobotSpecV04


def test_p0_seed_manifest_is_loadable_and_preserves_evidence_boundaries() -> None:
    manifest = load_seed_manifest(
        Path(__file__).parents[1] / "data" / "registry" / "seed_manifest.yaml"
    )

    assert manifest.schema_version == "g14.5"
    assert [artifact.id for artifact in manifest.artifacts] == [
        "differential-drive", "jetson-generic", "esp32", "serial-bridge",
        "ros2-control", "diff-drive-controller", "ld06", "realsense-d455",
        "nav2", "isaac-sim", "twist-twiststamped",
    ]
    assert all(artifact.verification.evidence_level not in {"E4", "E5"} for artifact in manifest.artifacts)
    assert all(artifact.source.url.startswith("https://") for artifact in manifest.artifacts)


def test_seed_manifest_rejects_real_hardware_claims() -> None:
    payload = {
        "artifacts": [{
            "id": "invalid-e4", "name": "Invalid", "artifact_type": "hardware_profile",
            "vendor": "Example", "model": "Example", "source": {
                "source_type": "official-repo", "url": "https://example.test/repo",
                "trust_level": "A", "license": {"spdx": "MIT", "redistribution": "allowed"},
                "retrieved_at": "2026-10-14",
            },
            "verification": {"evidence_level": "E4", "status": "pass", "target_evidence_level": "E4"},
            "provenance": "test",
        }],
    }

    with pytest.raises(ValueError, match="cannot claim E4 or E5"):
        SeedManifest.model_validate(payload)


def test_seed_manifest_compiles_into_reference_host_mcu_architecture_and_templates() -> None:
    registry = build_reference_registry(load_default_seed_manifest())
    architecture = ArchitectureResolver().resolve(
        ArchitectureResolutionRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["navigation", "motor-control", "encoder-feedback"],
                device_ids=["jetson-generic", "esp32"],
            ),
            hardware_profiles=registry.hardware_profiles,
        )
    )

    assert architecture.compatible is True
    assert architecture.plan is not None
    assert architecture.plan.architecture == "host-plus-mcu"
    assert architecture.plan.assignments[0].responsibility_ids == ["ros2-runtime", "nav2-runtime"]
    assert architecture.plan.assignments[1].responsibility_ids == ["motor-control", "encoder-feedback"]

    composition = CompositionPlanner().plan(
        CompositionPlanningRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["differential-drive", "planar-lidar", "rgbd-camera", "navigation"],
            ),
            architecture=ArchitecturePlan(architecture="host-plus-mcu"),
            registry=registry,
        )
    )
    assert composition.ready is True
    assert [component.id for component in composition.plan.components] == [
        "differential-drive", "lidar", "camera", "nav2"
    ]


def test_seed_manifest_preserves_mcu_only_navigation_conflict() -> None:
    registry = build_reference_registry(load_default_seed_manifest())

    result = ArchitectureResolver().resolve(
        ArchitectureResolutionRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["navigation", "motor-control"],
                requested_architecture="mcu-only",
                device_ids=["esp32"],
            ),
            hardware_profiles=registry.hardware_profiles,
        )
    )

    assert result.compatible is False
    assert result.status == "architecture-conflict"


def test_reference_robot_a_outputs_plans_dependencies_and_truthful_readiness() -> None:
    root = Path(__file__).parents[1] / "data" / "reference_robot_a"
    specification = ReferenceRobotSpec.model_validate(
        json.loads((root / "robot_spec.yaml").read_text(encoding="utf-8"))
    )

    result = ComponentLibraryPlanner().plan(load_default_seed_manifest(), specification)

    assert result.ready is True
    assert result.architecture_plan.model_dump() == json.loads(
        (root / "expected_architecture_plan.yaml").read_text(encoding="utf-8")
    )
    assert result.composition_plan.model_dump() == json.loads(
        (root / "expected_composition_plan.yaml").read_text(encoding="utf-8")
    )
    assert result.required_packages == ["ros2-control", "diff-drive-controller", "nav2"]
    assert result.required_drivers == ["ld06", "realsense-d455"]
    assert result.required_adapters == ["serial-bridge", "ros2-control", "twist-twiststamped"]
    assert result.hardware_readiness == "blocked"
    assert "esp32" in result.evidence_gaps
    assert len(result.deployment_checklist) == 4
    assert len(result.validation_plan) == 4


def test_reference_robot_a_blocks_an_unknown_seed_dependency() -> None:
    specification = ReferenceRobotSpec.model_validate({
        "id": "invalid-reference", "display_name": "Invalid reference",
        "robot_spec": {"robot_type": "differential-drive", "device_ids": ["jetson-generic"]},
        "package_ids": ["unknown-package"],
    })

    result = ComponentLibraryPlanner().plan(load_default_seed_manifest(), specification)

    assert result.ready is False
    assert result.missing_dependencies == ["unknown-package"]
    assert result.hardware_readiness == "blocked"
