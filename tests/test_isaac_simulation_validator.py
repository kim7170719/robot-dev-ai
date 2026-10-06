from agent.mvp_pipeline import (
    IsaacScenario,
    IsaacSimulationValidator,
    SimulationCommandEvidence,
)


def test_validate_m4_navigation_reports_pass_from_succeeded_goal() -> None:
    observed: list[tuple[str, ...]] = []

    def runner(arguments: tuple[str, ...]) -> SimulationCommandEvidence:
        observed.append(arguments)
        return SimulationCommandEvidence(
            command=" ".join(arguments),
            exit_code=0,
            stdout="Goal finished with status: SUCCEEDED\n",
        )

    result = IsaacSimulationValidator(runner=runner).validate(
        IsaacScenario.M4_NAVIGATION
    )

    assert observed[0][:4] == (
        "ros2",
        "action",
        "send_goal",
        "/navigate_to_pose",
    )
    assert result.status == "pass"
    assert result.evidence == ["navigation goal completed with SUCCEEDED"]
