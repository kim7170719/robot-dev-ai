from pathlib import Path

from starlette.testclient import TestClient

from agent.auto_debug.build_collector import BuildCommandCollector
from agent.auto_debug.collector import CommandEvidence, RosRuntimeCollector
from agent.auto_debug.diagnoser import BuildEvidence
from api.app import ProjectSummary, create_app


def test_project_summary_exposes_the_frozen_mvp_status() -> None:
    response = TestClient(
        create_app(
            project_summary=ProjectSummary(
                project_name="robot-dev-ai",
                branch="test-branch",
                ros_distro="jazzy",
                isaac_sim_version="4.5.0",
                latest_passed_gate="G12",
                evidence_scope="virtual-only",
                cosmos_status="deferred",
            )
        )
    ).get("/api/v1/project/summary")

    assert response.status_code == 200
    assert response.json() == {
        "project_name": "robot-dev-ai",
        "branch": "test-branch",
        "ros_distro": "jazzy",
        "isaac_sim_version": "4.5.0",
        "latest_passed_gate": "G12",
        "evidence_scope": "virtual-only",
        "cosmos_status": "deferred",
    }


def test_requirement_endpoint_returns_structured_spec_and_provenance() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/requirements/parse",
        json={"natural_language": "我要建立一台 NVIDIA 差速機器車，LiDAR + Camera，能自主導航。"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "specification": {
            "capability_ids": [
                "differential-drive",
                "planar-lidar",
                "rgb-camera",
                "navigation",
            ],
            "simulator": None,
        },
        "ambiguities": [],
        "provenance": {"capability_ids": "user"},
    }


def test_compatibility_endpoint_returns_selected_packages() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/compatibility/resolve",
        json={
            "registry": {
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
            },
            "request": {
                "hardware_id": "generic-diff-base",
                "specification": {"capability_ids": ["differential-drive"]},
                "ros_distro": "jazzy",
                "target_platform": "ubuntu-x86-64",
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "compatible": True,
        "status": "validated",
        "package_ids": ["diff-drive-controller"],
        "issues": [],
        "warnings": [],
    }


def test_template_preview_returns_rendered_files_without_workspace_writes() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/templates/preview",
        json={
            "registry": {
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
            },
            "request": {
                "hardware_id": "ydlidar-x4",
                "capability_id": "planar-lidar",
                "values": {"scan_topic": "/scan", "frame_id": "lidar_link"},
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "template_id": "lidar",
        "files": {
            "config/lidar.yaml": "scan_topic: /scan\nframe_id: lidar_link\n"
        },
    }


def test_runtime_snapshot_returns_read_only_collector_evidence() -> None:
    observed_commands: list[tuple[str, ...]] = []
    outputs = {
        ("ros2", "node", "list"): "/controller_server\n/robot_state_publisher\n",
        ("ros2", "topic", "list", "-t"): "/scan [sensor_msgs/msg/LaserScan]\n",
        ("ros2", "control", "list_controllers"): "diff_cont active\n",
        ("ros2", "topic", "echo", "/tf", "--once"): (
            "frame_id: odom\nchild_frame_id: base_link\n"
        ),
        ("ros2", "topic", "echo", "/tf_static", "--once"): (
            "frame_id: base_link\nchild_frame_id: lidar_link\n"
        ),
    }

    def collect(arguments: tuple[str, ...]) -> CommandEvidence:
        observed_commands.append(arguments)
        return CommandEvidence(
            command=" ".join(arguments), exit_code=0, stdout=outputs[arguments]
        )

    response = TestClient(
        create_app(
            runtime_collector_factory=lambda: RosRuntimeCollector(runner=collect)
        )
    ).get("/api/v1/runtime/snapshot")

    assert response.status_code == 200
    assert response.json()["nodes"] == ["/controller_server", "/robot_state_publisher"]
    assert response.json()["topic_types"] == {"/scan": "sensor_msgs/msg/LaserScan"}
    assert response.json()["controller_states"] == {"diff_cont": "active"}
    assert response.json()["tf_edges"] == [
        ["odom", "base_link"],
        ["base_link", "lidar_link"],
    ]
    assert observed_commands == list(outputs)


def test_workspace_plan_requires_confirmation_before_generating_files(
    tmp_path: Path,
) -> None:
    client = TestClient(create_app(workspace_root=tmp_path))
    request = {
        "output_name": "lidar_demo",
        "registry": {
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
        },
        "requests": [
            {
                "hardware_id": "ydlidar-x4",
                "capability_id": "planar-lidar",
                "values": {"scan_topic": "/scan", "frame_id": "lidar_link"},
            }
        ],
    }

    plan = client.post("/api/v1/workspaces/plan", json=request)

    assert plan.status_code == 200
    assert plan.json()["status"] == "awaiting-confirmation"
    assert plan.json()["files"] == {
        "config/lidar.yaml": "scan_topic: /scan\nframe_id: lidar_link\n"
    }
    assert not (tmp_path / "src" / "lidar_demo").exists()

    apply = client.post(
        "/api/v1/workspaces/apply",
        json={"confirmation_id": plan.json()["confirmation_id"], "confirmed": True},
    )

    assert apply.status_code == 200
    assert apply.json()["status"] == "generated"
    assert (tmp_path / "src" / "lidar_demo" / "config" / "lidar.yaml").read_text() == (
        "scan_topic: /scan\nframe_id: lidar_link\n"
    )


def test_workspace_build_requires_a_confirmed_generated_plan(tmp_path: Path) -> None:
    observed_commands: list[tuple[tuple[str, ...], Path]] = []

    def successful_build(
        arguments: tuple[str, ...], workspace: Path
    ) -> BuildEvidence:
        observed_commands.append((arguments, workspace))
        return BuildEvidence(command=" ".join(arguments), exit_code=0)

    client = TestClient(
        create_app(
            workspace_root=tmp_path,
            build_collector_factory=lambda workspace: BuildCommandCollector(
                workspace, runner=successful_build
            ),
        )
    )
    request = {
        "output_name": "lidar_demo",
        "registry": {
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
        },
        "requests": [
            {
                "hardware_id": "ydlidar-x4",
                "capability_id": "planar-lidar",
                "values": {"scan_topic": "/scan", "frame_id": "lidar_link"},
            }
        ],
    }

    plan = client.post("/api/v1/workspaces/plan", json=request)
    confirmation_id = plan.json()["confirmation_id"]

    before_apply = client.post(
        "/api/v1/workspaces/build",
        json={"confirmation_id": confirmation_id, "confirmed": True},
    )
    assert before_apply.status_code == 404

    apply = client.post(
        "/api/v1/workspaces/apply",
        json={"confirmation_id": confirmation_id, "confirmed": True},
    )
    assert apply.status_code == 200

    build = client.post(
        "/api/v1/workspaces/build",
        json={"confirmation_id": confirmation_id, "confirmed": True},
    )

    assert build.status_code == 200
    assert build.json()["status"] == "build-succeeded"
    assert build.json()["diagnosis"]["category"] == "build-succeeded"
    assert observed_commands == [
        (("colcon", "build", "--packages-select", "lidar_demo"), tmp_path)
    ]
