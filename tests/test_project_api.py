import io
from pathlib import Path

from starlette.testclient import TestClient

from agent.auto_debug.build_collector import BuildCommandCollector
from agent.auto_debug.collector import CommandEvidence, RosRuntimeCollector
from agent.auto_debug.simulation_view import SimulationFrame
from agent.auto_debug.diagnoser import BuildEvidence
from agent.mvp_pipeline import (
    IsaacScenario,
    IsaacSimulationValidator,
    MvpPipelineResult,
    SimulationCommandEvidence,
)
from api.app import ProjectSummary, create_app
from registry.models import RobotKnowledgeRegistry
from registry.v04 import RegistryDocumentV04
from registry.v06 import EvidenceEnvironment, EvidenceRecord, RegistryDocumentV06


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


def test_core_schema_summary_exposes_frozen_g125_contract() -> None:
    response = TestClient(create_app()).get("/api/v1/core/schema")

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "v0.4",
        "gate": "G12.5",
        "status": "frozen",
        "capabilities": [
            "architecture-resolution",
            "composition-planning",
            "adapter-resolution",
            "hardware-readiness",
            "mutation-safety",
            "unknown-component-flow",
        ],
        "next_gate": "G12.6",
    }


def test_evidence_endpoint_returns_contextual_summary_only() -> None:
    evidence_document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {"hardware": [{"id": "diff-base", "kind": "mobile-base", "vendor": "Example"}]}
            ),
        ),
        evidence_records=[
            EvidenceRecord(
                id="diff-base-e3", component_id="diff-base", evidence_level="E3",
                source_trust="A", status="pass",
                environment=EvidenceEnvironment(os="ubuntu-24-04", ros_distro="jazzy", cpu_arch="amd64"),
                provenance="m4-navigation",
            )
        ],
    )

    response = TestClient(create_app(evidence_document=evidence_document)).get(
        "/api/v1/evidence/diff-base"
    )

    assert response.status_code == 200
    assert response.json()["coverage_levels"] == ["E3"]
    assert response.json()["records"][0]["evidence_level"] == "E3"


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


def test_design_plan_recommends_only_validated_templates_without_writing() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/design/plan",
        json={
            "natural_language": "我要建立一台 NVIDIA 差速機器車，LiDAR + Camera，能自主導航。"
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready-for-build"
    assert body["resolution"]["package_ids"] == [
        "diff-drive-controller",
        "nav2-bringup",
        "lidar-driver",
        "camera-driver",
    ]
    assert [template["template_id"] for template in body["templates"]] == [
        "differential-drive",
        "lidar",
        "camera",
        "nav2",
    ]
    assert body["generated_package_root"] is None


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


def test_template_preview_returns_json_validation_error_for_missing_values() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/templates/preview",
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
                "capabilities": [
                    {
                        "id": "differential-drive",
                        "interface_ids": [],
                        "template_id": "differential-drive",
                    }
                ],
            },
            "request": {
                "hardware_id": "generic-diff-base",
                "capability_id": "differential-drive",
                "values": {"package_name": "demo_robot"},
            },
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "missing template value: cmd_vel_topic"


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


def test_simulation_view_returns_camera_frame_and_robot_pose() -> None:
    observed_sources: list[str] = []

    class FrameCollector:
        def collect_frame(self, source: str) -> SimulationFrame:
            observed_sources.append(source)
            return SimulationFrame(
                image_png_base64="iVBORw0KGgo=",
                width=64,
                height=48,
                x_m=1.25,
                y_m=-0.5,
                yaw_rad=0.3,
                source_topic="/camera/image_raw",
            )

    response = TestClient(
        create_app(simulation_frame_collector_factory=FrameCollector)
    ).get("/api/v1/simulation/frame?source=webcam")

    assert response.status_code == 200
    assert response.json() == {
        "image_png_base64": "iVBORw0KGgo=",
        "width": 64,
        "height": 48,
        "x_m": 1.25,
        "y_m": -0.5,
        "yaw_rad": 0.3,
        "source_topic": "/camera/image_raw",
        "pose_available": True,
    }
    assert observed_sources == ["webcam"]


def test_simulation_view_returns_typed_unavailable_evidence() -> None:
    class UnavailableFrameCollector:
        def collect_frame(self, source: str) -> SimulationFrame:
            raise RuntimeError("timed out waiting for /camera/image_raw and /odom")

    response = TestClient(
        create_app(simulation_frame_collector_factory=UnavailableFrameCollector)
    ).get("/api/v1/simulation/frame")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "timed out waiting for /camera/image_raw and /odom"
    }


def test_simulation_stream_returns_a_bounded_mjpeg_response() -> None:
    class Process:
        stdout = io.BytesIO(b"--frame\r\nContent-Type: image/jpeg\r\n\r\ntest-frame\r\n")

        @staticmethod
        def poll() -> int:
            return 0

        @staticmethod
        def terminate() -> None:
            raise AssertionError("completed process should not terminate")

    class StreamCollector:
        def start(self, source: str) -> Process:
            assert source == "webcam"
            return Process()

    response = TestClient(
        create_app(simulation_mjpeg_stream_factory=StreamCollector)
    ).get("/api/v1/simulation/stream?source=webcam")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "multipart/x-mixed-replace; boundary=frame"
    )
    assert response.content.startswith(b"--frame\r\nContent-Type: image/jpeg")


def test_fixed_navigation_validation_requires_confirmation() -> None:
    observed_commands: list[tuple[str, ...]] = []

    def validate(arguments: tuple[str, ...]) -> SimulationCommandEvidence:
        observed_commands.append(arguments)
        return SimulationCommandEvidence(
            command=" ".join(arguments),
            exit_code=0,
            stdout="Goal finished with status: SUCCEEDED\n",
        )

    client = TestClient(
        create_app(
            simulation_validator_factory=lambda: IsaacSimulationValidator(
                runner=validate
            )
        )
    )

    rejected = client.post("/api/v1/validation/m4-navigation", json={})
    assert rejected.status_code == 422

    response = client.post(
        "/api/v1/validation/m4-navigation", json={"confirmed": True}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "pass"
    assert response.json()["scenario"] == "m4-navigation"
    assert observed_commands == [
        (
            "ros2",
            "action",
            "send_goal",
            "/navigate_to_pose",
            "nav2_msgs/action/NavigateToPose",
            "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}",
        )
    ]


def test_full_mvp_run_returns_pipeline_and_runtime_evidence(tmp_path: Path) -> None:
    received_requests: list[str] = []
    received_workspaces: list[Path] = []

    class SuccessfulPipeline:
        def run(self, natural_language: str) -> MvpPipelineResult:
            received_requests.append(natural_language)
            return MvpPipelineResult.model_validate(
                {
                    "status": "build-succeeded",
                    "requirements": {
                        "specification": {"capability_ids": ["differential-drive"]},
                        "ambiguities": [],
                        "provenance": {"capability_ids": "user"},
                    },
                    "build_diagnosis": {"category": "build-succeeded"},
                }
            )

    def runtime_evidence(arguments: tuple[str, ...]) -> CommandEvidence:
        return CommandEvidence(command=" ".join(arguments), exit_code=0)

    client = TestClient(
        create_app(
            mvp_pipeline_factory=lambda workspace: (
                received_workspaces.append(workspace) or SuccessfulPipeline()
            ),
            runtime_collector_factory=lambda: RosRuntimeCollector(
                runner=runtime_evidence
            ),
        )
    )

    response = client.post(
        "/api/v1/mvp/full-run",
        json={
            "natural_language": "Build a differential-drive robot.",
            "confirmed": True,
            "include_validation": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["pipeline"]["status"] == "build-succeeded"
    assert response.json()["workspace_lifecycle"] == "ephemeral-cleaned"
    assert response.json()["validation"] is None
    assert received_requests == ["Build a differential-drive robot."]
    assert len(received_workspaces) == 1
    assert not received_workspaces[0].exists()


def test_repair_proposal_returns_a_reviewable_diff_without_writing_files() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/repairs/propose",
        json={
            "path": "src/demo_robot/package.xml",
            "contents": '<package format="3">\n  <name>demo_robot</name>\n</package>\n',
            "missing_dependency": "geometry_msgs",
        },
    )

    assert response.status_code == 200
    assert response.json()["category"] == "missing-package-dependency"
    assert response.json()["safe_to_apply"] is False
    assert "+  <depend>geometry_msgs</depend>" in response.json()["proposed_diff"]


def test_gui_entrypoint_exposes_all_m14_views() -> None:
    response = TestClient(create_app()).get("/")

    assert response.status_code == 200
    for view_name in (
        "Overview",
        "Design",
        "Build",
        "Run",
        "Diagnose",
        "Evidence",
        "驗證資料的真實範圍",
    ):
        assert view_name in response.text


def test_lan_read_only_mode_allows_dashboard_but_blocks_all_post_apis() -> None:
    """LAN presentation must not expose execution or workspace-write routes."""
    client = TestClient(create_app(read_only=True))

    summary = client.get("/api/v1/project/summary")
    landing = client.get("/")
    assert summary.status_code == 200
    assert landing.status_code == 200
    for path in (
        "/api/v1/requirements/parse",
        "/api/v1/design/plan",
        "/api/v1/compatibility/resolve",
        "/api/v1/templates/preview",
        "/api/v1/validation/m4-navigation",
        "/api/v1/mvp/full-run",
        "/api/v1/repairs/propose",
        "/api/v1/workspaces/plan",
        "/api/v1/workspaces/apply",
        "/api/v1/workspaces/build",
    ):
        blocked = client.post(path, json={})
        assert blocked.status_code == 403
        assert blocked.json() == {"detail": "M14 is running in read-only mode."}


def test_app_factory_uses_the_read_only_environment_switch(monkeypatch) -> None:
    monkeypatch.setenv("ROBOT_DEV_AI_READ_ONLY", "true")

    response = TestClient(create_app()).post(
        "/api/v1/requirements/parse",
        json={"natural_language": "Build a differential-drive robot."},
    )

    assert response.status_code == 403


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
