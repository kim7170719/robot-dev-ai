from agent.architecture_resolver import ArchitectureResolutionRequest, ArchitectureResolver
from registry.v04 import HardwareProfileV04, RobotSpecV04


def test_resolve_assigns_navigation_to_linux_host_and_motor_control_to_mcu() -> None:
    result = ArchitectureResolver().resolve(
        ArchitectureResolutionRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["navigation", "motor-control", "encoder-feedback"],
                device_ids=["jetson-orin-nano", "esp32-motor-board"],
            ),
            hardware_profiles=[
                HardwareProfileV04(
                    device_id="jetson-orin-nano",
                    device_class="edge-compute",
                    capability_ids=["ros2-runtime", "nav2-runtime"],
                    verification_state="experimental",
                    provenance="test",
                ),
                HardwareProfileV04(
                    device_id="esp32-motor-board",
                    device_class="mcu",
                    capability_ids=["motor-control", "encoder-feedback"],
                    verification_state="experimental",
                    provenance="test",
                ),
            ],
        )
    )

    assert result.compatible is True
    assert result.status == "resolved"
    assert result.issues == []
    assert result.plan.model_dump() == {
        "architecture": "host-plus-mcu",
        "assignments": [
            {
                "device_id": "jetson-orin-nano",
                "responsibility_ids": ["ros2-runtime", "nav2-runtime"],
            },
            {
                "device_id": "esp32-motor-board",
                "responsibility_ids": ["motor-control", "encoder-feedback"],
            },
        ],
        "evidence_status": "not-tested",
    }


def test_resolve_blocks_mcu_only_navigation_request() -> None:
    result = ArchitectureResolver().resolve(
        ArchitectureResolutionRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["navigation", "motor-control"],
                device_ids=["esp32-motor-board"],
            ),
            hardware_profiles=[
                HardwareProfileV04(
                    device_id="esp32-motor-board",
                    device_class="mcu",
                    capability_ids=["motor-control"],
                    verification_state="experimental",
                    provenance="test",
                )
            ],
        )
    )

    assert result.compatible is False
    assert result.status == "architecture-conflict"
    assert result.plan is None
    assert result.issues == [
        "architecture conflict: navigation requires a Linux host with ros2-runtime"
    ]


def test_resolve_honors_explicit_mcu_only_architecture_for_motor_control() -> None:
    result = ArchitectureResolver().resolve(
        ArchitectureResolutionRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["motor-control"],
                requested_architecture="mcu-only",
                device_ids=["jetson-orin-nano", "esp32-motor-board"],
            ),
            hardware_profiles=[
                HardwareProfileV04(
                    device_id="jetson-orin-nano",
                    device_class="edge-compute",
                    capability_ids=["ros2-runtime", "nav2-runtime"],
                    verification_state="experimental",
                    provenance="test",
                ),
                HardwareProfileV04(
                    device_id="esp32-motor-board",
                    device_class="mcu",
                    capability_ids=["motor-control"],
                    verification_state="experimental",
                    provenance="test",
                ),
            ],
        )
    )

    assert result.compatible is True
    assert result.plan.model_dump()["architecture"] == "mcu-only"
    assert result.plan.model_dump()["assignments"] == [
        {"device_id": "esp32-motor-board", "responsibility_ids": ["motor-control"]}
    ]


def test_resolve_honors_explicit_remote_host_plus_mcu_architecture() -> None:
    result = ArchitectureResolver().resolve(
        ArchitectureResolutionRequest(
            specification=RobotSpecV04(
                robot_type="differential-drive",
                capability_ids=["navigation", "motor-control"],
                requested_architecture="remote-host-plus-mcu",
                device_ids=["jetson-orin-nano", "esp32-motor-board"],
            ),
            hardware_profiles=[
                HardwareProfileV04(
                    device_id="jetson-orin-nano",
                    device_class="edge-compute",
                    capability_ids=["ros2-runtime", "nav2-runtime"],
                    verification_state="experimental",
                    provenance="test",
                ),
                HardwareProfileV04(
                    device_id="esp32-motor-board",
                    device_class="mcu",
                    capability_ids=["motor-control"],
                    verification_state="experimental",
                    provenance="test",
                ),
            ],
        )
    )

    assert result.compatible is True
    assert result.plan.model_dump()["architecture"] == "remote-host-plus-mcu"
