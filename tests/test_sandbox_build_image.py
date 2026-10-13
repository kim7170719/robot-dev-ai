from pathlib import Path


def test_ros_jazzy_build_image_is_explicit_and_has_colcon() -> None:
    dockerfile = (Path(__file__).parents[1] / "docker" / "Dockerfile.sandbox-ros-jazzy-build").read_text()

    assert "FROM ros:jazzy-ros-base" in dockerfile
    assert "python3-colcon-common-extensions" in dockerfile
    assert "latest" not in dockerfile
