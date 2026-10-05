import pytest
from pydantic import ValidationError

from registry.models import RobotKnowledgeRegistry


def valid_registry() -> dict:
    return {
        "hardware": [
            {
                "id": "realsense-d435i",
                "kind": "camera",
                "vendor": "Intel",
                "capability_ids": ["rgbd-camera"],
            }
        ],
        "drivers": [
            {
                "id": "realsense-ros",
                "hardware_id": "realsense-d435i",
                "ros_distro": "jazzy",
            }
        ],
        "interfaces": [
            {
                "id": "camera-image",
                "topic": "/camera/color/image_raw",
                "message_type": "sensor_msgs/msg/Image",
            }
        ],
        "capabilities": [
            {
                "id": "rgbd-camera",
                "interface_ids": ["camera-image"],
            }
        ],
        "packages": [
            {
                "id": "isaac-ros-image-proc",
                "required_capability_ids": ["rgbd-camera"],
            }
        ],
        "compatibility": [
            {
                "hardware_id": "realsense-d435i",
                "package_id": "isaac-ros-image-proc",
                "status": "validated",
            }
        ],
    }


def test_registry_accepts_traceable_hardware_to_package_path() -> None:
    registry = RobotKnowledgeRegistry.model_validate(valid_registry())

    assert registry.model_dump()["compatibility"] == [
        {
                "hardware_id": "realsense-d435i",
                "package_id": "isaac-ros-image-proc",
                "status": "validated",
                "target_platforms": [],
                "note": None,
        }
    ]


def test_registry_rejects_compatibility_reference_to_unknown_hardware() -> None:
    data = valid_registry()
    data["compatibility"][0]["hardware_id"] = "unknown-camera"

    with pytest.raises(ValidationError, match="unknown hardware"):
        RobotKnowledgeRegistry.model_validate(data)


def test_registry_rejects_package_requirement_without_capability() -> None:
    data = valid_registry()
    data["packages"][0]["required_capability_ids"] = ["stereo-depth"]

    with pytest.raises(ValidationError, match="unknown capability"):
        RobotKnowledgeRegistry.model_validate(data)
