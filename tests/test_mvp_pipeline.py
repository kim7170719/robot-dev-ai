from pathlib import Path

from agent.auto_debug import BuildCommandCollector, BuildEvidence
from agent.mvp_pipeline import MvpPipeline
from registry.models import RobotKnowledgeRegistry


def test_run_prepares_a_validated_diff_drive_navigation_mvp(tmp_path: Path) -> None:
    registry = RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "generic-diff-base",
                    "kind": "mobile-base",
                    "vendor": "Robot Dev AI",
                    "capability_ids": [
                        "differential-drive",
                        "planar-lidar",
                        "rgb-camera",
                        "navigation",
                    ],
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
                {
                    "id": "differential-drive",
                    "interface_ids": [],
                    "template_id": "differential-drive",
                },
                {
                    "id": "navigation",
                    "interface_ids": [],
                    "template_id": "nav2",
                },
                {
                    "id": "planar-lidar",
                    "interface_ids": [],
                    "template_id": "lidar",
                },
                {
                    "id": "rgb-camera",
                    "interface_ids": [],
                    "template_id": "camera",
                },
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
                {
                    "id": "lidar-driver",
                    "required_capability_ids": ["planar-lidar"],
                },
                {
                    "id": "camera-driver",
                    "required_capability_ids": ["rgb-camera"],
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
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "lidar-driver",
                    "status": "validated",
                },
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "camera-driver",
                    "status": "validated",
                },
            ],
        }
    )

    result = MvpPipeline(
        registry=registry,
        hardware_id="generic-diff-base",
        template_root=Path("templates"),
        output_root=tmp_path,
    ).run("我要建立一台 NVIDIA 差速機器車，LiDAR + Camera，能自主導航。")

    assert result.status == "ready-for-build"
    assert result.resolution.package_ids == [
        "diff-drive-controller",
        "nav2-bringup",
        "lidar-driver",
        "camera-driver",
    ]
    assert [template.template_id for template in result.templates] == [
        "differential-drive",
        "lidar",
        "camera",
        "nav2",
    ]
    assert "setup.py" in result.templates[0].files
    assert "config/lidar.yaml" in result.templates[1].files
    assert "config/camera.yaml" in result.templates[2].files
    assert "config/nav2_params.yaml" in result.templates[3].files
    assert result.generated_package_root == tmp_path / "mvp_diff_drive"
    assert (tmp_path / "mvp_diff_drive" / "setup.py").is_file()
    assert (tmp_path / "mvp_diff_drive" / "config" / "nav2_params.yaml").is_file()
    assert (tmp_path / "mvp_diff_drive" / "config" / "lidar.yaml").is_file()
    assert (tmp_path / "mvp_diff_drive" / "config" / "camera.yaml").is_file()


def test_run_reports_build_success_from_restricted_collector(tmp_path: Path) -> None:
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
            "drivers": [
                {
                    "id": "generic-diff-driver",
                    "hardware_id": "generic-diff-base",
                    "ros_distro": "jazzy",
                }
            ],
            "capabilities": [
                {
                    "id": "differential-drive",
                    "interface_ids": [],
                    "template_id": "differential-drive",
                }
            ],
            "packages": [
                {
                    "id": "diff-drive-controller",
                    "required_capability_ids": ["differential-drive"],
                }
            ],
            "compatibility": [
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "diff-drive-controller",
                    "status": "validated",
                }
            ],
        }
    )

    def runner(arguments: tuple[str, ...], workspace: Path) -> BuildEvidence:
        assert arguments == (
            "colcon",
            "build",
            "--packages-select",
            "mvp_diff_drive",
        )
        assert workspace == tmp_path
        return BuildEvidence(command=" ".join(arguments), exit_code=0)

    result = MvpPipeline(
        registry=registry,
        hardware_id="generic-diff-base",
        template_root=Path("templates"),
        output_root=tmp_path / "src",
        build_collector=BuildCommandCollector(tmp_path, runner=runner),
    ).run("Build a differential-drive robot.")

    assert result.status == "build-succeeded"
    assert result.build_diagnosis.category == "build-succeeded"
