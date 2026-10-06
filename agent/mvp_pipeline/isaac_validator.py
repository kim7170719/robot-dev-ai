"""Fixed-scenario Isaac Sim validation for the frozen MVP."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IsaacScenario(str, Enum):
    """The pre-approved simulation scenarios available to the MVP."""

    M4_NAVIGATION = "m4-navigation"


class SimulationCommandEvidence(BaseModel):
    """Captured evidence from a fixed simulation validation command."""

    model_config = ConfigDict(extra="forbid")

    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""


class SimulationValidationResult(BaseModel):
    """A clear, reviewable PASS or FAIL outcome."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(pattern=r"^(pass|fail)$")
    scenario: IsaacScenario
    evidence: list[str] = Field(default_factory=list)
    command: SimulationCommandEvidence


SimulationRunner = Callable[[tuple[str, ...]], SimulationCommandEvidence]


class IsaacSimulationValidator:
    """Validate only frozen Isaac Sim scenarios without shell execution."""

    def __init__(self, runner: SimulationRunner | None = None) -> None:
        self._runner = runner or _run

    def validate(self, scenario: IsaacScenario) -> SimulationValidationResult:
        evidence = self._runner(_COMMANDS[scenario])
        if evidence.exit_code == 0 and "SUCCEEDED" in evidence.stdout:
            return SimulationValidationResult(
                status="pass",
                scenario=scenario,
                evidence=["navigation goal completed with SUCCEEDED"],
                command=evidence,
            )
        return SimulationValidationResult(
            status="fail",
            scenario=scenario,
            evidence=[
                "navigation goal did not report SUCCEEDED",
                f"exit code: {evidence.exit_code}",
            ],
            command=evidence,
        )


_COMMANDS: dict[IsaacScenario, tuple[str, ...]] = {
    IsaacScenario.M4_NAVIGATION: (
        "ros2",
        "action",
        "send_goal",
        "/navigate_to_pose",
        "nav2_msgs/action/NavigateToPose",
        (
            "{pose: {header: {frame_id: 'map'}, pose: {position: "
            "{x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
        ),
    ),
}


def _run(arguments: tuple[str, ...]) -> SimulationCommandEvidence:
    try:
        completed = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            shell=False,
            text=True,
            timeout=90,
        )
    except FileNotFoundError:
        return SimulationCommandEvidence(
            command=" ".join(arguments),
            exit_code=127,
            stderr="command not found: ros2",
        )
    except subprocess.TimeoutExpired:
        return SimulationCommandEvidence(
            command=" ".join(arguments),
            exit_code=124,
            stderr="simulation validation timed out after 90 seconds",
        )
    return SimulationCommandEvidence(
        command=" ".join(arguments),
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
