from agent.auto_debug import CommandEvidence, RosCommandCollector


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
