"""Allowlisted, read-only ROS command collection."""

from __future__ import annotations

import subprocess
import re
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


InspectionCommand = Literal[
    "ros2-node-list",
    "ros2-topic-list-types",
    "ros2-control-list-controllers",
    "ros2-tf-once",
    "ros2-tf-static-once",
]

COMMANDS: dict[InspectionCommand, tuple[str, ...]] = {
    "ros2-node-list": ("ros2", "node", "list"),
    "ros2-topic-list-types": ("ros2", "topic", "list", "-t"),
    "ros2-control-list-controllers": ("ros2", "control", "list_controllers"),
    "ros2-tf-once": ("ros2", "topic", "echo", "/tf", "--once"),
    "ros2-tf-static-once": ("ros2", "topic", "echo", "/tf_static", "--once"),
}


class CommandEvidence(BaseModel):
    """Captured output from one allowlisted read-only command."""

    model_config = ConfigDict(extra="forbid")

    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""


class RosRuntimeSnapshot(BaseModel):
    """Structured evidence from the fixed read-only ROS inspection set."""

    model_config = ConfigDict(extra="forbid")

    commands: dict[InspectionCommand, CommandEvidence]
    nodes: list[str] = Field(default_factory=list)
    topic_types: dict[str, str] = Field(default_factory=dict)
    controller_states: dict[str, str] = Field(default_factory=dict)
    tf_edges: list[tuple[str, str]] = Field(default_factory=list)


CommandRunner = Callable[[tuple[str, ...]], CommandEvidence]


class RosCommandCollector:
    """Run only fixed ROS inspection commands without a shell."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or _run

    def collect(self, command: InspectionCommand) -> CommandEvidence:
        return self._runner(COMMANDS[command])


class RosRuntimeCollector(RosCommandCollector):
    """Collect a complete non-mutating ROS runtime snapshot."""

    def collect_snapshot(self) -> RosRuntimeSnapshot:
        commands = {
            command: self.collect(command)
            for command in COMMANDS
        }
        return RosRuntimeSnapshot(
            commands=commands,
            nodes=_parse_nodes(commands["ros2-node-list"]),
            topic_types=_parse_topic_types(commands["ros2-topic-list-types"]),
            controller_states=_parse_controller_states(
                commands["ros2-control-list-controllers"]
            ),
            tf_edges=(
                _parse_tf_edges(commands["ros2-tf-once"])
                + _parse_tf_edges(commands["ros2-tf-static-once"])
            ),
        )


def _parse_nodes(evidence: CommandEvidence) -> list[str]:
    if evidence.exit_code != 0:
        return []
    return [line.strip() for line in evidence.stdout.splitlines() if line.strip()]


def _parse_topic_types(evidence: CommandEvidence) -> dict[str, str]:
    if evidence.exit_code != 0:
        return {}
    topic_types: dict[str, str] = {}
    for line in evidence.stdout.splitlines():
        topic, separator, message_type = line.partition(" [")
        if separator and message_type.endswith("]"):
            topic_types[topic] = message_type.removesuffix("]")
    return topic_types


def _parse_controller_states(evidence: CommandEvidence) -> dict[str, str]:
    if evidence.exit_code != 0:
        return {}
    controller_states: dict[str, str] = {}
    for line in evidence.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 2:
            controller_states[fields[0]] = fields[-1]
    return controller_states


def _parse_tf_edges(evidence: CommandEvidence) -> list[tuple[str, str]]:
    if evidence.exit_code != 0:
        return []
    return [
        (parent.strip(), child.strip())
        for parent, child in re.findall(
            r"(?ms)^[ \t]*frame_id:\s*['\\\"]?([^'\\\"\n]+?)['\\\"]?\s*$"
            r".*?^[ \t]*child_frame_id:\s*['\\\"]?([^'\\\"\n]+?)['\\\"]?\s*$",
            evidence.stdout,
        )
    ]


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
