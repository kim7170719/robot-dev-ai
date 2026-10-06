from agent.compatibility_resolver import CompatibilityResolver, ResolutionRequest
from agent.requirement_agent import RequirementAgent
from agent.schemas import RobotSpecification
from registry.models import RobotKnowledgeRegistry


def validated_navigation_registry() -> RobotKnowledgeRegistry:
    return RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "generic-diff-base",
                    "kind": "mobile-base",
                    "vendor": "Robot Dev AI",
                    "capability_ids": ["differential-drive", "navigation"],
                }
            ],
            "drivers": [
                {
                    "id": "generic-diff-driver",
                    "hardware_id": "generic-diff-base",
                    "ros_distro": "jazzy",
                }
            ],
            "capabilities": [
                {"id": "differential-drive", "interface_ids": []},
                {"id": "navigation", "interface_ids": []},
            ],
            "packages": [
                {
                    "id": "diff-drive-controller",
                    "required_capability_ids": ["differential-drive"],
                },
                {
                    "id": "nav2-bringup",
                    "required_capability_ids": ["navigation"],
                },
            ],
            "compatibility": [
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "diff-drive-controller",
                    "status": "validated",
                },
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "nav2-bringup",
                    "status": "validated",
                },
            ],
        }
    )


def test_resolve_selects_validated_packages_for_a_jazzy_robot_specification() -> None:
    result = CompatibilityResolver().resolve(
        validated_navigation_registry(),
        ResolutionRequest(
            hardware_id="generic-diff-base",
            specification=RobotSpecification(
                capability_ids=["differential-drive", "navigation"]
            ),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is True
    assert result.package_ids == ["diff-drive-controller", "nav2-bringup"]
    assert result.issues == []


def test_resolve_accepts_structured_specification_from_requirement_agent() -> None:
    specification = RequirementAgent().parse(
        "Build a differential-drive robot with Nav2."
    ).specification

    result = CompatibilityResolver().resolve(
        validated_navigation_registry(),
        ResolutionRequest(
            hardware_id="generic-diff-base",
            specification=specification,
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is True
    assert result.package_ids == ["diff-drive-controller", "nav2-bringup"]


def test_resolve_reports_missing_hardware_capability() -> None:
    result = CompatibilityResolver().resolve(
        validated_navigation_registry(),
        ResolutionRequest(
            hardware_id="generic-diff-base",
            specification=RobotSpecification(capability_ids=["rgb-camera"]),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is False
    assert result.package_ids == []
    assert result.issues == ["hardware lacks required capabilities: rgb-camera"]


def test_resolve_excludes_package_blocked_on_target_platform() -> None:
    payload = validated_navigation_registry().model_dump()
    payload["compatibility"][0]["target_platforms"] = ["jetson"]
    registry = RobotKnowledgeRegistry.model_validate(payload)

    result = CompatibilityResolver().resolve(
        registry,
        ResolutionRequest(
            hardware_id="generic-diff-base",
            specification=RobotSpecification(
                capability_ids=["differential-drive", "navigation"]
            ),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is False
    assert result.package_ids == ["nav2-bringup"]
    assert result.issues == [
        "package diff-drive-controller is unsupported on ubuntu-x86-64"
    ]


def test_resolve_reports_when_hardware_has_no_jazzy_driver() -> None:
    payload = validated_navigation_registry().model_dump()
    payload["drivers"][0]["ros_distro"] = "humble"
    registry = RobotKnowledgeRegistry.model_validate(payload)

    result = CompatibilityResolver().resolve(
        registry,
        ResolutionRequest(
            hardware_id="generic-diff-base",
            specification=RobotSpecification(capability_ids=["differential-drive"]),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is False
    assert result.issues == [
        "hardware generic-diff-base has no driver for ROS jazzy"
    ]


def test_resolve_selects_validated_conversion_for_message_type_mismatch() -> None:
    registry = RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "stamped-base",
                    "kind": "mobile-base",
                    "vendor": "Robot Dev AI",
                    "capability_ids": ["differential-drive", "navigation"],
                }
            ],
            "drivers": [
                {
                    "id": "stamped-driver",
                    "hardware_id": "stamped-base",
                    "ros_distro": "jazzy",
                }
            ],
            "interfaces": [
                {
                    "id": "cmd-vel-twist",
                    "topic": "/cmd_vel",
                    "message_type": "geometry_msgs/msg/Twist",
                },
                {
                    "id": "cmd-vel-twist-stamped",
                    "topic": "/cmd_vel",
                    "message_type": "geometry_msgs/msg/TwistStamped",
                },
            ],
            "capabilities": [
                {
                    "id": "differential-drive",
                    "interface_ids": ["cmd-vel-twist-stamped"],
                },
                {"id": "navigation", "interface_ids": []},
            ],
            "packages": [
                {
                    "id": "diff-drive-controller",
                    "required_capability_ids": ["differential-drive"],
                },
                {
                    "id": "nav2-controller",
                    "required_capability_ids": ["navigation"],
                    "required_interface_ids": ["cmd-vel-twist"],
                },
                {"id": "twist-stamper", "required_capability_ids": []},
            ],
            "compatibility": [
                {
                    "hardware_id": "stamped-base",
                    "package_id": "diff-drive-controller",
                    "status": "validated",
                },
                {
                    "hardware_id": "stamped-base",
                    "package_id": "nav2-controller",
                    "status": "validated",
                },
                {
                    "hardware_id": "stamped-base",
                    "package_id": "twist-stamper",
                    "status": "validated",
                },
            ],
            "conversions": [
                {
                    "id": "twist-to-stamped",
                    "source_interface_id": "cmd-vel-twist",
                    "target_interface_id": "cmd-vel-twist-stamped",
                    "package_id": "twist-stamper",
                }
            ],
        }
    )

    result = CompatibilityResolver().resolve(
        registry,
        ResolutionRequest(
            hardware_id="stamped-base",
            specification=RobotSpecification(
                capability_ids=["differential-drive", "navigation"]
            ),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is True
    assert result.package_ids == [
        "diff-drive-controller",
        "nav2-controller",
        "twist-stamper",
    ]
    assert result.issues == []


def test_resolve_reports_capability_without_a_registered_package_dependency() -> None:
    payload = validated_navigation_registry().model_dump()
    payload["packages"] = [payload["packages"][0]]
    payload["compatibility"] = [payload["compatibility"][0]]
    registry = RobotKnowledgeRegistry.model_validate(payload)

    result = CompatibilityResolver().resolve(
        registry,
        ResolutionRequest(
            hardware_id="generic-diff-base",
            specification=RobotSpecification(capability_ids=["navigation"]),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
        ),
    )

    assert result.compatible is False
    assert result.package_ids == []
    assert result.issues == ["no package declares capability: navigation"]


def test_resolve_marks_turing_isaac_ros_as_experimental_with_evidence() -> None:
    registry = RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "image-pipeline-host",
                    "kind": "compute-host",
                    "vendor": "Robot Dev AI",
                    "capability_ids": ["gpu-image-resize"],
                }
            ],
            "drivers": [
                {
                    "id": "nvidia-container-runtime",
                    "hardware_id": "image-pipeline-host",
                    "ros_distro": "jazzy",
                }
            ],
            "capabilities": [
                {"id": "gpu-image-resize", "interface_ids": []},
            ],
            "packages": [
                {
                    "id": "isaac-ros-image-proc",
                    "required_capability_ids": ["gpu-image-resize"],
                    "minimum_gpu_architecture": "ampere",
                }
            ],
            "compatibility": [
                {
                    "hardware_id": "image-pipeline-host",
                    "package_id": "isaac-ros-image-proc",
                    "status": "experimental",
                    "note": "M5 resize smoke test passed on RTX 2080 Ti.",
                }
            ],
        }
    )

    result = CompatibilityResolver().resolve(
        registry,
        ResolutionRequest(
            hardware_id="image-pipeline-host",
            specification=RobotSpecification(capability_ids=["gpu-image-resize"]),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
            gpu_architecture="turing",
        ),
    )

    assert result.compatible is True
    assert result.status == "experimental"
    assert result.package_ids == ["isaac-ros-image-proc"]
    assert result.issues == []
    assert result.warnings == [
        "package isaac-ros-image-proc requires Ampere+; Turing is experimental"
    ]


def test_resolve_blocks_gpu_below_package_minimum_without_experimental_evidence() -> None:
    payload = {
        "hardware": [
            {
                "id": "image-pipeline-host",
                "kind": "compute-host",
                "vendor": "Robot Dev AI",
                "capability_ids": ["gpu-image-resize"],
            }
        ],
        "drivers": [
            {
                "id": "nvidia-container-runtime",
                "hardware_id": "image-pipeline-host",
                "ros_distro": "jazzy",
            }
        ],
        "capabilities": [{"id": "gpu-image-resize", "interface_ids": []}],
        "packages": [
            {
                "id": "isaac-ros-image-proc",
                "required_capability_ids": ["gpu-image-resize"],
                "minimum_gpu_architecture": "ampere",
            }
        ],
        "compatibility": [
            {
                "hardware_id": "image-pipeline-host",
                "package_id": "isaac-ros-image-proc",
                "status": "validated",
            }
        ],
    }
    registry = RobotKnowledgeRegistry.model_validate(payload)

    result = CompatibilityResolver().resolve(
        registry,
        ResolutionRequest(
            hardware_id="image-pipeline-host",
            specification=RobotSpecification(capability_ids=["gpu-image-resize"]),
            ros_distro="jazzy",
            target_platform="ubuntu-x86-64",
            gpu_architecture="turing",
        ),
    )

    assert result.compatible is False
    assert result.status == "blocked"
    assert result.package_ids == []
    assert result.issues == ["package isaac-ros-image-proc requires Ampere+"]
