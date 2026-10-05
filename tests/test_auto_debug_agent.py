from agent.auto_debug import (
    AutoDebugAgent,
    BuildEvidence,
    CommandEvidence,
    ControllerEvidence,
    NodeEvidence,
    PackageManifestEvidence,
    RosGraphEvidence,
    TfEvidence,
)


def test_diagnose_missing_ros_package_from_colcon_output() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        BuildEvidence(
            command="colcon build --packages-select demo_robot",
            exit_code=1,
            stderr=(
                "CMake Error at CMakeLists.txt:14 (find_package):\n"
                "  Could not find a package configuration file provided by "
                "\"geometry_msgs\".\n"
            ),
        )
    )

    assert diagnosis.category == "missing-ros-package"
    assert diagnosis.evidence == ["geometry_msgs"]
    assert diagnosis.suggested_actions == [
        "sudo apt install ros-jazzy-geometry-msgs",
        "source /opt/ros/jazzy/setup.bash and rebuild",
    ]
    assert diagnosis.safe_to_apply is False
    assert diagnosis.report.command == "colcon build --packages-select demo_robot"
    assert diagnosis.report.exit_code == 1
    assert diagnosis.report.proposed_diff is None


def test_diagnose_successful_build_as_non_failure() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        BuildEvidence(
            command="colcon build --packages-select demo_robot",
            exit_code=0,
        )
    )

    assert diagnosis.category == "build-succeeded"
    assert diagnosis.evidence == []
    assert diagnosis.suggested_actions == []


def test_diagnose_missing_package_from_ros_launch_output() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        BuildEvidence(
            command="ros2 launch nav2_bringup navigation_launch.py",
            exit_code=1,
            stderr="PackageNotFoundError: \"package 'nav2_bringup' not found\"",
        )
    )

    assert diagnosis.category == "missing-ros-package"
    assert diagnosis.evidence == ["nav2_bringup"]
    assert diagnosis.suggested_actions[0] == "sudo apt install ros-jazzy-nav2-bringup"


def test_diagnose_topic_message_type_mismatch_from_graph_snapshot() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        RosGraphEvidence(
            topic="/cmd_vel",
            observed_message_type="geometry_msgs/msg/Twist",
            required_message_type="geometry_msgs/msg/TwistStamped",
        )
    )

    assert diagnosis.category == "topic-type-mismatch"
    assert diagnosis.evidence == [
        "/cmd_vel: geometry_msgs/msg/Twist != geometry_msgs/msg/TwistStamped"
    ]
    assert diagnosis.suggested_actions == [
        "add or configure a validated Twist-to-TwistStamped conversion node"
    ]


def test_diagnose_missing_required_tf_edge() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        TfEvidence(
            required_parent="map",
            required_child="odom",
            observed_edges=[("odom", "base_link")],
        )
    )

    assert diagnosis.category == "missing-tf-transform"
    assert diagnosis.evidence == ["missing transform: map -> odom"]
    assert diagnosis.suggested_actions == [
        "start the node that publishes map -> odom before navigation"
    ]


def test_diagnose_inactive_required_controller() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        ControllerEvidence(
            required_active=["joint_state_broadcaster", "diff_drive_controller"],
            observed_states={
                "joint_state_broadcaster": "active",
                "diff_drive_controller": "inactive",
            },
        )
    )

    assert diagnosis.category == "inactive-controller"
    assert diagnosis.evidence == ["diff_drive_controller: inactive"]
    assert diagnosis.suggested_actions == [
        "activate controller diff_drive_controller before commanding the robot"
    ]


def test_diagnose_stops_when_repair_budget_is_exhausted() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        BuildEvidence(
            command="colcon build --packages-select demo_robot",
            exit_code=1,
            stderr='Could not find a package configuration file provided by "geometry_msgs".',
            repair_attempt=3,
            max_repair_attempts=3,
        )
    )

    assert diagnosis.category == "repair-limit-reached"
    assert diagnosis.evidence == ["repair attempts: 3/3"]
    assert diagnosis.suggested_actions == [
        "stop automatic repair and preserve this failure evidence for review"
    ]
    assert diagnosis.safe_to_apply is False


def test_diagnose_timeout_from_allowlisted_ros_collector() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        CommandEvidence(
            command="ros2 control list_controllers",
            exit_code=124,
            stderr="command timed out after 10 seconds",
        )
    )

    assert diagnosis.category == "ros-command-timeout"
    assert diagnosis.evidence == ["ros2 control list_controllers"]
    assert diagnosis.suggested_actions == [
        "inspect controller_manager availability before retrying ros2 control"
    ]


def test_diagnose_missing_required_ros_node() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        NodeEvidence(
            required_nodes=["/controller_manager"],
            observed_nodes=["/tm_smooth_controller"],
        )
    )

    assert diagnosis.category == "missing-ros-node"
    assert diagnosis.evidence == ["missing node: /controller_manager"]
    assert diagnosis.suggested_actions == [
        "start /controller_manager before querying ros2 control"
    ]


def test_diagnose_proposes_but_does_not_apply_package_manifest_dependency_diff() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        PackageManifestEvidence(
            path="src/demo_robot/package.xml",
            contents=(
                '<package format="3">\n'
                "  <name>demo_robot</name>\n"
                "</package>\n"
            ),
            missing_dependency="geometry_msgs",
        )
    )

    assert diagnosis.category == "missing-package-dependency"
    assert diagnosis.safe_to_apply is False
    assert "  <depend>geometry_msgs</depend>" in diagnosis.report.proposed_diff
    assert diagnosis.report.proposed_diff.startswith(
        "--- src/demo_robot/package.xml\n+++ src/demo_robot/package.xml"
    )


def test_diagnose_refuses_manifest_proposal_outside_project_path() -> None:
    diagnosis = AutoDebugAgent().diagnose(
        PackageManifestEvidence(
            path="../package.xml",
            contents="<package></package>\n",
            missing_dependency="geometry_msgs",
        )
    )

    assert diagnosis.category == "unknown-build-failure"
    assert diagnosis.report.proposed_diff is None
