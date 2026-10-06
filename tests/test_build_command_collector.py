from pathlib import Path

import pytest

from agent.auto_debug import BuildCommandCollector, BuildEvidence


def test_collect_builds_only_selected_packages_without_a_shell() -> None:
    observed: list[tuple[tuple[str, ...], Path]] = []

    def runner(arguments: tuple[str, ...], workspace: Path) -> BuildEvidence:
        observed.append((arguments, workspace))
        return BuildEvidence(
            command=" ".join(arguments),
            exit_code=0,
            stdout="Summary: 2 packages finished\n",
        )

    evidence = BuildCommandCollector(
        workspace=Path("/workspace/ros_ws"),
        runner=runner,
    ).collect(["simple_diff_robot", "simple_diff_nav"])

    assert observed == [
        (
            (
                "colcon",
                "build",
                "--packages-select",
                "simple_diff_robot",
                "simple_diff_nav",
            ),
            Path("/workspace/ros_ws"),
        )
    ]
    assert evidence.exit_code == 0
    assert evidence.command == (
        "colcon build --packages-select simple_diff_robot simple_diff_nav"
    )


def test_collect_rejects_unsafe_package_name_before_running_command() -> None:
    was_called = False

    def runner(arguments: tuple[str, ...], workspace: Path) -> BuildEvidence:
        nonlocal was_called
        was_called = True
        return BuildEvidence(command=" ".join(arguments), exit_code=0)

    collector = BuildCommandCollector(
        workspace=Path("/workspace/ros_ws"),
        runner=runner,
    )

    with pytest.raises(ValueError, match="valid ROS package names"):
        collector.collect(["simple_diff_robot; touch /tmp/unwanted"])

    assert was_called is False
