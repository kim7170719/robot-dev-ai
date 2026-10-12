import pytest
from pydantic import ValidationError

from registry.v04 import (
    ArchitectureAssignment,
    ArchitecturePlan,
    CompositionComponent,
    CompositionPlan,
    ResourceProfile,
    RobotSpecV04,
    Constraint,
    RegistryDocumentV04,
    SoftwareProfileV04,
    migrate_v03_registry,
)
from registry.models import RobotKnowledgeRegistry


def test_migrate_v03_registry_preserves_legacy_facts_without_inventing_verification() -> None:
    migrated = migrate_v03_registry(
        {
            "hardware": [
                {
                    "id": "esp32-motor-board",
                    "kind": "mcu",
                    "vendor": "Example Robotics",
                    "capability_ids": ["motor-control"],
                }
            ],
            "capabilities": [
                {"id": "motor-control", "interface_ids": []},
            ],
        }
    )

    assert migrated.schema_version == "v0.4"
    assert migrated.source_schema_version == "v0.3"
    assert migrated.registry.hardware[0].id == "esp32-motor-board"
    assert [profile.model_dump() for profile in migrated.hardware_profiles] == [
        {
            "device_id": "esp32-motor-board",
            "device_class": "mcu",
            "capability_ids": ["motor-control"],
            "transport_ids": [],
            "driver_ids": [],
            "constraint_ids": [],
            "firmware_required": False,
            "verification_state": "unknown",
            "limitations": [],
            "provenance": "migrated-v0.3",
        }
    ]


def test_v04_schema_models_keep_architecture_composition_and_resource_separate() -> None:
    request = RobotSpecV04(
        robot_type="differential-drive",
        capability_ids=["navigation", "motor-control"],
        device_ids=["jetson-orin-nano", "esp32-motor-board"],
    )
    resources = ResourceProfile(
        id="jetson-orin-nano",
        cpu_arch="aarch64",
        ram_gb=8,
        storage_gb=64,
        power_budget_w=15,
    )
    architecture = ArchitecturePlan(
        architecture="host-plus-mcu",
        assignments=[
            ArchitectureAssignment(
                device_id="jetson-orin-nano",
                responsibility_ids=["ros2-runtime", "nav2-runtime"],
            ),
            ArchitectureAssignment(
                device_id="esp32-motor-board",
                responsibility_ids=["motor-control"],
            ),
        ],
    )
    composition = CompositionPlan(
        components=[
            CompositionComponent(kind="template", id="base-diff-drive"),
            CompositionComponent(
                kind="adapter",
                id="serial-bridge",
                device_id="esp32-motor-board",
            ),
        ]
    )

    assert request.requested_architecture == "auto"
    assert resources.model_dump()["power_budget_w"] == 15.0
    assert architecture.evidence_status == "not-tested"
    assert composition.model_dump()["components"][1]["kind"] == "adapter"


def test_v04_registry_links_hardware_to_declared_driver_transport_and_constraints() -> None:
    document = RegistryDocumentV04(
        source_schema_version="v0.3",
        registry=RobotKnowledgeRegistry.model_validate(
            {
                "hardware": [
                    {
                        "id": "esp32-motor-board",
                        "kind": "mcu",
                        "vendor": "Example Robotics",
                        "capability_ids": ["motor-control"],
                    }
                ],
                "capabilities": [{"id": "motor-control", "interface_ids": []}],
            }
        ),
        software_profiles=[
            SoftwareProfileV04(
                id="micro-ros-driver",
                kind="driver",
                version="1.0.0",
                verification_state="experimental",
                provenance="vendor-sdk",
            )
        ],
        constraints=[
            Constraint(
                id="serial-transport",
                kind="transport",
                expected_value="uart",
                provenance="datasheet",
            ),
            Constraint(
                id="firmware-version",
                kind="firmware",
                expected_value="1.2.3",
                provenance="vendor-sdk",
            ),
        ],
        hardware_profiles=[
            {
                "device_id": "esp32-motor-board",
                "device_class": "mcu",
                "capability_ids": ["motor-control"],
                "transport_ids": ["serial-transport"],
                "driver_ids": ["micro-ros-driver"],
                "constraint_ids": ["firmware-version"],
                "firmware_required": True,
                "verification_state": "experimental",
                "provenance": "lab-inventory",
            }
        ],
    )

    profile = document.hardware_profiles[0]
    assert profile.firmware_required is True
    assert profile.driver_ids == ["micro-ros-driver"]
    assert document.constraints[0].kind == "transport"


def test_v04_registry_rejects_hardware_profile_with_unknown_transport() -> None:
    with pytest.raises(ValidationError, match="unknown transport"):
        RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {
                    "hardware": [
                        {
                            "id": "esp32-motor-board",
                            "kind": "mcu",
                            "vendor": "Example Robotics",
                            "capability_ids": ["motor-control"],
                        }
                    ],
                    "capabilities": [{"id": "motor-control", "interface_ids": []}],
                }
            ),
            hardware_profiles=[
                {
                    "device_id": "esp32-motor-board",
                    "device_class": "mcu",
                    "transport_ids": ["serial-transport"],
                    "verification_state": "unknown",
                    "provenance": "test",
                }
            ],
        )
