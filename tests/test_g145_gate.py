"""G14.5 acceptance tests over the P0 seed library; no external source is run."""

from agent.component_library import ComponentLibraryPlanner, load_default_reference_robot_spec
from agent.unknown_component import UnknownComponentRequest, UnknownComponentResolver
from registry.g145 import load_default_seed_manifest


def test_t1_known_software_composition_is_deterministic() -> None:
    result = ComponentLibraryPlanner().plan(
        load_default_seed_manifest(), load_default_reference_robot_spec()
    )

    assert result.ready is True
    assert [component.id for component in result.composition_plan.components] == [
        "differential-drive", "lidar", "camera", "nav2"
    ]


def test_t2_host_mcu_architecture_assigns_linux_and_realtime_work() -> None:
    result = ComponentLibraryPlanner().plan(
        load_default_seed_manifest(), load_default_reference_robot_spec()
    )

    assert result.architecture_plan.architecture == "host-plus-mcu"
    assert result.architecture_plan.assignments[0].responsibility_ids == ["ros2-runtime", "nav2-runtime"]
    assert result.architecture_plan.assignments[1].responsibility_ids == ["motor-control", "encoder-feedback"]


def test_t3_full_reference_robot_has_reviewable_outputs() -> None:
    result = ComponentLibraryPlanner().plan(
        load_default_seed_manifest(), load_default_reference_robot_spec()
    )

    assert result.required_packages == ["ros2-control", "diff-drive-controller", "nav2"]
    assert result.required_drivers == ["ld06", "realsense-d455"]
    assert result.required_adapters == ["serial-bridge", "ros2-control", "twist-twiststamped"]
    assert result.deployment_checklist
    assert result.validation_plan
    assert result.hardware_readiness == "blocked"


def test_t4_dynamic_component_templates_work_without_a_full_robot_template() -> None:
    result = ComponentLibraryPlanner().plan(
        load_default_seed_manifest(), load_default_reference_robot_spec()
    )

    assert len(result.composition_plan.components) == 4
    assert all(component.kind == "template" for component in result.composition_plan.components)


def test_t5_unknown_component_is_blocked_not_invented() -> None:
    result = UnknownComponentResolver().resolve(
        UnknownComponentRequest(device_id="unknown-lidar")
    )

    assert result.status == "blocked"
    assert result.requires_human_approval is False


def test_t7_manifest_does_not_promote_documented_or_simulated_records_to_real() -> None:
    manifest = load_default_seed_manifest()

    assert all(artifact.verification.evidence_level not in {"E4", "E5"} for artifact in manifest.artifacts)
    assert all("real-hardware" not in " ".join(artifact.limitations).lower() or artifact.verification.evidence_level != "E4" for artifact in manifest.artifacts)


def test_t7_evidence_gaps_keep_unready_seed_artifacts_visible() -> None:
    result = ComponentLibraryPlanner().plan(
        load_default_seed_manifest(), load_default_reference_robot_spec()
    )

    assert "esp32" in result.evidence_gaps
    assert "ld06" in result.evidence_gaps
    assert result.hardware_readiness == "blocked"


def test_t8_reference_plan_has_no_side_effect_authority() -> None:
    result = ComponentLibraryPlanner().plan(
        load_default_seed_manifest(), load_default_reference_robot_spec()
    )

    assert result.ready is True
    assert result.issues == []
    assert result.hardware_readiness == "blocked"
