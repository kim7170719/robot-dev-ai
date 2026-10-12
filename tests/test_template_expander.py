from pathlib import Path

import pytest

from agent.template_engine import (
    CompositionExpansionRequest,
    ExpansionRequest,
    TemplateExpander,
)
from registry.models import RobotKnowledgeRegistry
from registry.v04 import CompositionComponent, CompositionPlan


def lidar_registry() -> RobotKnowledgeRegistry:
    return RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "ydlidar-x4",
                    "kind": "lidar",
                    "vendor": "YDLIDAR",
                    "capability_ids": ["planar-lidar"],
                }
            ],
            "capabilities": [
                {
                    "id": "planar-lidar",
                    "interface_ids": [],
                    "template_id": "lidar",
                }
            ],
        }
    )


def test_hardware_capability_selects_and_expands_lidar_template() -> None:
    expander = TemplateExpander(template_root=Path("templates"))

    result = expander.expand(
        lidar_registry(),
        ExpansionRequest(
            hardware_id="ydlidar-x4",
            capability_id="planar-lidar",
            values={"scan_topic": "/scan", "frame_id": "lidar_link"},
        ),
    )

    assert result.template_id == "lidar"
    assert result.files == {
        "config/lidar.yaml": "scan_topic: /scan\nframe_id: lidar_link\n"
    }


def test_expansion_rejects_capability_not_declared_by_hardware() -> None:
    expander = TemplateExpander(template_root=Path("templates"))

    with pytest.raises(ValueError, match="does not declare capability"):
        expander.expand(
            lidar_registry(),
            ExpansionRequest(
                hardware_id="ydlidar-x4",
                capability_id="rgbd-camera",
                values={},
            ),
        )


def test_differential_drive_expands_package_name_in_paths_and_contents() -> None:
    registry = RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "generic-diff-base",
                    "kind": "mobile-base",
                    "vendor": "Robot Dev AI",
                    "capability_ids": ["differential-drive"],
                }
            ],
            "capabilities": [
                {
                    "id": "differential-drive",
                    "interface_ids": [],
                    "template_id": "differential-drive",
                }
            ],
        }
    )

    result = TemplateExpander(template_root=Path("templates")).expand(
        registry,
        ExpansionRequest(
            hardware_id="generic-diff-base",
            capability_id="differential-drive",
            values={
                "package_name": "demo_diff_drive",
                "base_frame": "base_link",
                "cmd_vel_topic": "/cmd_vel",
                "wheel_radius_m": "0.05",
                "wheel_separation_m": "0.30",
            },
        ),
    )

    assert result.files["resource/demo_diff_drive"] == "demo_diff_drive\n"
    assert "name='demo_diff_drive'" in result.files["setup.py"]
    controller = result.files["demo_diff_drive/controller.py"]
    assert 'Twist, "/cmd_vel", self._observe_cmd_vel, 10' in controller
    assert 'UInt32, "/demo_diff_drive/cmd_vel_observed", 10' in controller
    assert "<exec_depend>geometry_msgs</exec_depend>" in result.files["package.xml"]
    assert "<exec_depend>std_msgs</exec_depend>" in result.files["package.xml"]
    launch = result.files["launch/controller.launch.py"]
    assert 'FindPackageShare("demo_diff_drive")' in launch
    assert '"config", "controller.yaml"' in launch


@pytest.mark.parametrize(
    ("capability_id", "template_id", "values", "expected_file", "expected_text"),
    [
        (
            "rgb-camera",
            "camera",
            {
                "frame_id": "camera_link",
                "image_topic": "/camera/image_raw",
                "camera_info_topic": "/camera/camera_info",
            },
            "config/camera.yaml",
            "frame_id: camera_link",
        ),
        (
            "navigation",
            "nav2",
            {
                "base_frame": "base_link",
                "odom_frame": "odom",
                "map_frame": "map",
                "odom_topic": "/odom",
            },
            "config/nav2_params.yaml",
            "global_frame_id: map",
        ),
        (
            "gpu-image-resize",
            "isaac-ros-image-proc",
            {
                "input_image_topic": "/camera/image_raw",
                "input_camera_info_topic": "/camera/camera_info",
                "output_width": "480",
                "output_height": "288",
            },
            "launch/image_proc.launch.py",
            '"output_width": 480',
        ),
    ],
)
def test_capability_templates_expand_deterministically(
    capability_id: str,
    template_id: str,
    values: dict[str, str],
    expected_file: str,
    expected_text: str,
) -> None:
    registry = RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "test-hardware",
                    "kind": "test",
                    "vendor": "Robot Dev AI",
                    "capability_ids": [capability_id],
                }
            ],
            "capabilities": [
                {
                    "id": capability_id,
                    "interface_ids": [],
                    "template_id": template_id,
                }
            ],
        }
    )

    result = TemplateExpander(template_root=Path("templates")).expand(
        registry,
        ExpansionRequest(
            hardware_id="test-hardware",
            capability_id=capability_id,
            values=values,
        ),
    )

    assert expected_text in result.files[expected_file]


def test_expansion_writes_all_files_below_requested_output_root(tmp_path: Path) -> None:
    result = TemplateExpander(template_root=Path("templates")).expand(
        lidar_registry(),
        ExpansionRequest(
            hardware_id="ydlidar-x4",
            capability_id="planar-lidar",
            values={"scan_topic": "/scan", "frame_id": "lidar_link"},
        ),
    )

    TemplateExpander(template_root=Path("templates")).write(result, tmp_path)

    assert (tmp_path / "config/lidar.yaml").read_text(encoding="utf-8") == (
        "scan_topic: /scan\nframe_id: lidar_link\n"
    )


def test_composition_plan_expands_ordered_components_without_registry_lookup() -> None:
    result = TemplateExpander(template_root=Path("templates")).expand_composition(
        CompositionExpansionRequest(
            plan=CompositionPlan(
                components=[
                    CompositionComponent(
                        kind="template", id="lidar", device_id="front-lidar"
                    ),
                    CompositionComponent(
                        kind="template", id="camera", device_id="front-camera"
                    ),
                ]
            ),
            component_values=[
                {"scan_topic": "/scan", "frame_id": "lidar_link"},
                {
                    "frame_id": "camera_link",
                    "image_topic": "/camera/image_raw",
                    "camera_info_topic": "/camera/camera_info",
                },
            ],
        )
    )

    assert [component.template_id for component in result.components] == [
        "lidar",
        "camera",
    ]
    assert result.files == {
        "config/lidar.yaml": "scan_topic: /scan\nframe_id: lidar_link\n",
        "config/camera.yaml": (
            "camera:\n"
            "  ros__parameters:\n"
            "    frame_id: camera_link\n"
            "    image_topic: /camera/image_raw\n"
            "    camera_info_topic: /camera/camera_info\n"
        ),
    }


def test_composition_plan_rejects_colliding_component_output_paths() -> None:
    request = CompositionExpansionRequest(
        plan=CompositionPlan(
            components=[
                CompositionComponent(kind="template", id="lidar", device_id="front-lidar"),
                CompositionComponent(kind="template", id="lidar", device_id="rear-lidar"),
            ]
        ),
        component_values=[
            {"scan_topic": "/scan/front", "frame_id": "front_lidar_link"},
            {"scan_topic": "/scan/rear", "frame_id": "rear_lidar_link"},
        ],
    )

    with pytest.raises(ValueError, match="component output path collision: config/lidar.yaml"):
        TemplateExpander(template_root=Path("templates")).expand_composition(request)
