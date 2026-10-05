"""Allowlisted, read-only ROS command collection."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict


InspectionCommand = Literal[
    "ros2-node-list",
    "ros2-topic-list-types",
    "ros2-control-list-controllers",
]

COMMANDS: dict[InspectionCommand, tuple[str, ...]] = {
    "ros2-node-list": ("ros2", "node", "list"),
    "ros2-topic-list-types": ("ros2", "topic", "list", "-t"),
    "ros2-control-list-controllers": ("ros2", "control", "list_controllers"),
}


class CommandEvidence(BaseModel):
    """Captured output from one allowlisted read-only command."""

    model_config = ConfigDict(extra="forbid")

    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""


CommandRunner = Callable[[tuple[str, ...]], CommandEvidence]


class RosCommandCollector:
    """Run only fixed ROS inspection commands without a shell."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or _run

    def collect(self, command: InspectionCommand) -> CommandEvidence:
        return self._runner(COMMANDS[command])


def _run(arguments: tuple[str, ...]) -> CommandEvidence:
    try:
        completed = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            shell=False,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return CommandEvidence(
            command=" ".join(arguments),
            exit_code=127,
            stderr=f"command not found: {arguments[0]}",
        )
    except subprocess.TimeoutExpired:
        return CommandEvidence(
            command=" ".join(arguments),
            exit_code=124,
            stderr="command timed out after 10 seconds",
        )
    return CommandEvidence(
        command=" ".join(arguments),
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
