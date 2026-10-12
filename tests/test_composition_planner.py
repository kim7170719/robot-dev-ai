from agent.composition_planner import CompositionPlanner, CompositionPlanningRequest
from registry.models import RobotKnowledgeRegistry
from registry.v04 import (
    ArchitecturePlan,
    HardwareProfileV04,
    RegistryDocumentV04,
    RobotSpecV04,
)


def test_plan_composes_known_components_in_requested_capability_order() -> None:
    registry = RegistryDocumentV04(
        source_schema_version="v0.3",
        registry=RobotKnowledgeRegistry.model_validate(
            {
                "hardware": [
                    {
                        "id": "diff-base",
                        "kind": "mobile-base",
                        "vendor": "Example",
                        "capability_ids": ["differential-drive"],
                    },
                    {
                        "id": "ld06-lidar",
                        "kind": "lidar",
                        "vendor": "LDROBOT",
                        "capability_ids": ["planar-lidar"],
                    },
                    {
                        "id": "jetson-orin-nano",
                        "kind": "edge-compute",
                        "vendor": "NVIDIA",
                        "capability_ids": ["navigation"],
                    },
                ],
                "capabilities": [
                    {
                        "id": "differential-drive",
                        "template_id": "base-diff-drive",
                    },
                    {"id": "planar-lidar", "template_id": "sensor-ld06"},
                    {"id": "navigation", "template_id": "navigation-nav2"},
                ],
            }
        ),
        hardware_profiles=[
            HardwareProfileV04(
                device_id="diff-base",
                device_class="mobile-base",
                capability_ids=["differential-drive"],
                verification_state="experimental",
                provenance="test",
            ),
            HardwareProfileV04(
                device_id="ld06-lidar",
                device_class="lidar",
                capability_ids=["planar-lidar"],
                verification_state="experimental",
                provenance="test",
            ),
            HardwareProfileV04(
                device_id="jetson-orin-nano",
                device_class="edge-compute",
                capability_ids=["navigation"],
                verification_state="experimental",
                provenance="test",
            ),
        ],
    )

    result = CompositionPlanner().plan(
        CompositionPlanningRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["differential-drive", "planar-lidar", "navigation"],
            ),
            architecture=ArchitecturePlan(architecture="linux-onboard"),
            registry=registry,
        )
    )

    assert result.ready is True
    assert result.issues == []
    assert result.plan.model_dump() == {
        "components": [
            {"kind": "template", "id": "base-diff-drive", "device_id": "diff-base"},
            {"kind": "template", "id": "sensor-ld06", "device_id": "ld06-lidar"},
            {"kind": "template", "id": "navigation-nav2", "device_id": "jetson-orin-nano"},
        ],
        "evidence_status": "not-tested",
    }


def test_plan_blocks_known_capability_without_component_template() -> None:
    result = CompositionPlanner().plan(
        CompositionPlanningRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["motor-control"],
            ),
            architecture=ArchitecturePlan(architecture="mcu-only"),
            registry=RegistryDocumentV04(
                source_schema_version="v0.3",
                registry=RobotKnowledgeRegistry.model_validate(
                    {
                        "hardware": [
                            {
                                "id": "esp32-motor-board",
                                "kind": "mcu",
                                "vendor": "Example",
                                "capability_ids": ["motor-control"],
                            }
                        ],
                        "capabilities": [{"id": "motor-control"}],
                    }
                ),
                hardware_profiles=[
                    HardwareProfileV04(
                        device_id="esp32-motor-board",
                        device_class="mcu",
                        capability_ids=["motor-control"],
                        verification_state="unknown",
                        provenance="test",
                    )
                ],
            ),
        )
    )

    assert result.ready is False
    assert result.plan is None
    assert result.issues == ["capability motor-control has no component template"]
