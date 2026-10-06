from starlette.testclient import TestClient

from api.app import create_app


def test_project_summary_exposes_the_frozen_mvp_status() -> None:
    response = TestClient(create_app()).get("/api/v1/project/summary")

    assert response.status_code == 200
    assert response.json() == {
        "project_name": "robot-dev-ai",
        "branch": "feature/m12-full-mvp",
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
