from pathlib import Path

import pytest

from agent.template_engine import ExpansionRequest, TemplateExpander
from registry.models import RobotKnowledgeRegistry


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
