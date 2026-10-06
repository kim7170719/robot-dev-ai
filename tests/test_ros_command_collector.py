from agent.auto_debug import (
    CommandEvidence,
    RosCommandCollector,
    RosRuntimeCollector,
)


def test_collect_node_list_uses_only_the_allowlisted_ros_command() -> None:
    observed_arguments: list[tuple[str, ...]] = []

    def runner(arguments: tuple[str, ...]) -> CommandEvidence:
        observed_arguments.append(arguments)
        return CommandEvidence(
            command=" ".join(arguments),
            exit_code=0,
            stdout="/controller_manager\n",
        )

    evidence = RosCommandCollector(runner=runner).collect("ros2-node-list")

    assert observed_arguments == [("ros2", "node", "list")]
    assert evidence.exit_code == 0
    assert evidence.stdout == "/controller_manager\n"


def test_collect_snapshot_returns_parsed_read_only_ros_runtime_evidence() -> None:
    outputs = {
        ("ros2", "node", "list"): "/controller_manager\n/nav2_controller\n",
        ("ros2", "topic", "list", "-t"): (
            "/cmd_vel [geometry_msgs/msg/Twist]\n"
            "/scan [sensor_msgs/msg/LaserScan]\n"
        ),
        ("ros2", "control", "list_controllers"): (
            "joint_state_broadcaster "
            "joint_state_broadcaster/JointStateBroadcaster active\n"
            "diff_drive_controller "
            "diff_drive_controller/DiffDriveController inactive\n"
        ),
        ("ros2", "topic", "echo", "/tf", "--once"): (
            "transforms:\n"
            "- header:\n"
            "    frame_id: map\n"
            "  child_frame_id: odom\n"
        ),
        ("ros2", "topic", "echo", "/tf_static", "--once"): (
            "transforms:\n"
            "- header:\n"
            "    frame_id: base_link\n"
            "  child_frame_id: laser\n"
        ),
    }

    def runner(arguments: tuple[str, ...]) -> CommandEvidence:
        return CommandEvidence(
            command=" ".join(arguments),
            exit_code=0,
            stdout=outputs[arguments],
        )

    snapshot = RosRuntimeCollector(runner=runner).collect_snapshot()

    assert snapshot.nodes == ["/controller_manager", "/nav2_controller"]
    assert snapshot.topic_types == {
        "/cmd_vel": "geometry_msgs/msg/Twist",
        "/scan": "sensor_msgs/msg/LaserScan",
    }
    assert snapshot.controller_states == {
        "joint_state_broadcaster": "active",
        "diff_drive_controller": "inactive",
    }
    assert snapshot.tf_edges == [("map", "odom"), ("base_link", "laser")]
    assert list(snapshot.commands) == [
        "ros2-node-list",
        "ros2-topic-list-types",
        "ros2-control-list-controllers",
        "ros2-tf-once",
        "ros2-tf-static-once",
    ]
