from starlette.testclient import TestClient

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
