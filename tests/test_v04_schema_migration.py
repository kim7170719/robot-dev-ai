from registry.v04 import (
    ArchitectureAssignment,
    ArchitecturePlan,
    CompositionComponent,
    CompositionPlan,
    ResourceProfile,
    RobotSpecV04,
    migrate_v03_registry,
)


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
