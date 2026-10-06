"""Evidence-based, non-mutating diagnosis for robot development failures."""

from __future__ import annotations

import difflib
import re
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .collector import CommandEvidence, RosRuntimeSnapshot


class BuildEvidence(BaseModel):
    """The observable result of one build command."""

    model_config = ConfigDict(extra="forbid")

    command: str = Field(min_length=1)
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    repair_attempt: int = Field(default=0, ge=0)
    max_repair_attempts: int = Field(default=3, ge=1)


class RosGraphEvidence(BaseModel):
    """One observed topic and the interface required by its consumer."""

    model_config = ConfigDict(extra="forbid")

    topic: str = Field(pattern=r"^/")
    observed_message_type: str = Field(min_length=3)
    required_message_type: str = Field(min_length=3)


class TfEvidence(BaseModel):
    """Observed TF edges against one required parent-to-child transform."""

    model_config = ConfigDict(extra="forbid")

    required_parent: str = Field(min_length=1)
    required_child: str = Field(min_length=1)
    observed_edges: list[tuple[str, str]] = Field(default_factory=list)


class ControllerEvidence(BaseModel):
    """Controller-manager state needed before motion commands are safe."""

    model_config = ConfigDict(extra="forbid")

    required_active: list[str] = Field(default_factory=list)
    observed_states: dict[str, str] = Field(default_factory=dict)


class NodeEvidence(BaseModel):
    """ROS node graph observed against nodes required by a workflow."""

    model_config = ConfigDict(extra="forbid")

    required_nodes: list[str] = Field(default_factory=list)
    observed_nodes: list[str] = Field(default_factory=list)


class RuntimeRequirements(BaseModel):
    """Declared ROS runtime conditions needed by a robot workflow."""

    model_config = ConfigDict(extra="forbid")

    required_nodes: list[str] = Field(default_factory=list)
    required_topic_types: dict[str, str] = Field(default_factory=dict)
    required_active_controllers: list[str] = Field(default_factory=list)
    required_tf_edges: list[tuple[str, str]] = Field(default_factory=list)


class PackageManifestEvidence(BaseModel):
    """A package manifest and a dependency proven missing by build evidence."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    contents: str
    missing_dependency: str = Field(min_length=1)


class FailureReport(BaseModel):
    """Serializable evidence retained when diagnosis stops for review."""

    model_config = ConfigDict(extra="forbid")

    command: str | None = None
    exit_code: int | None = None
    category: str
    evidence: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    repair_attempt: int | None = None
    max_repair_attempts: int | None = None
    proposed_diff: str | None = None


class DiagnosisResult(BaseModel):
    """A bounded recommendation derived from observed evidence."""

    model_config = ConfigDict(extra="forbid")

    category: Literal[
        "build-succeeded",
        "missing-ros-package",
        "missing-package-dependency",
        "missing-tf-transform",
        "inactive-controller",
        "missing-ros-node",
        "repair-limit-reached",
        "ros-command-timeout",
        "topic-type-mismatch",
        "unknown-build-failure",
    ]
    evidence: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    proposed_diff: str | None = None
    safe_to_apply: bool = False
    report: FailureReport | None = None


class AutoDebugAgent:
    """Classify known build failures without changing the host."""

    def diagnose(
        self,
        evidence: (
            BuildEvidence
            | CommandEvidence
            | RosGraphEvidence
            | TfEvidence
            | ControllerEvidence
            | NodeEvidence
            | PackageManifestEvidence
        ),
    ) -> DiagnosisResult:
        if isinstance(evidence, RosGraphEvidence):
            result = self._diagnose_ros_graph(evidence)
        elif isinstance(evidence, TfEvidence):
            result = self._diagnose_tf(evidence)
        elif isinstance(evidence, ControllerEvidence):
            result = self._diagnose_controllers(evidence)
        elif isinstance(evidence, NodeEvidence):
            result = self._diagnose_nodes(evidence)
        elif isinstance(evidence, PackageManifestEvidence):
            result = self._diagnose_manifest(evidence)
        elif isinstance(evidence, CommandEvidence):
            result = self._diagnose_command(evidence)
        else:
            result = self._diagnose_build(evidence)
        return self._with_report(evidence, result)

    def diagnose_snapshot(
        self,
        snapshot: RosRuntimeSnapshot,
        requirements: RuntimeRequirements,
    ) -> list[DiagnosisResult]:
        """Diagnose failed read-only collection commands from one snapshot."""

        diagnoses = [
            self.diagnose(evidence)
            for evidence in snapshot.commands.values()
            if evidence.exit_code != 0
        ]
        if requirements.required_nodes:
            node_diagnosis = self.diagnose(
                NodeEvidence(
                    required_nodes=requirements.required_nodes,
                    observed_nodes=snapshot.nodes,
                )
            )
            if node_diagnosis.category != "unknown-build-failure":
                diagnoses.append(node_diagnosis)
        for topic, required_message_type in requirements.required_topic_types.items():
            observed_message_type = snapshot.topic_types.get(topic)
            if observed_message_type is None:
                continue
            topic_diagnosis = self.diagnose(
                RosGraphEvidence(
                    topic=topic,
                    observed_message_type=observed_message_type,
                    required_message_type=required_message_type,
                )
            )
            if topic_diagnosis.category != "unknown-build-failure":
                diagnoses.append(topic_diagnosis)
        controller_command = snapshot.commands.get(
            "ros2-control-list-controllers"
        )
        if (
            requirements.required_active_controllers
            and (controller_command is None or controller_command.exit_code == 0)
        ):
            controller_diagnosis = self.diagnose(
                ControllerEvidence(
                    required_active=requirements.required_active_controllers,
                    observed_states=snapshot.controller_states,
                )
            )
            if controller_diagnosis.category != "unknown-build-failure":
                diagnoses.append(controller_diagnosis)
        tf_commands = [
            snapshot.commands.get("ros2-tf-once"),
            snapshot.commands.get("ros2-tf-static-once"),
        ]
        if (
            requirements.required_tf_edges
            and all(command is None or command.exit_code == 0 for command in tf_commands)
        ):
            for required_parent, required_child in requirements.required_tf_edges:
                tf_diagnosis = self.diagnose(
                    TfEvidence(
                        required_parent=required_parent,
                        required_child=required_child,
                        observed_edges=snapshot.tf_edges,
                    )
                )
                if tf_diagnosis.category != "unknown-build-failure":
                    diagnoses.append(tf_diagnosis)
        return diagnoses

    @staticmethod
    def _with_report(
        evidence: (
            BuildEvidence
            | CommandEvidence
            | RosGraphEvidence
            | TfEvidence
            | ControllerEvidence
            | NodeEvidence
            | PackageManifestEvidence
        ),
        result: DiagnosisResult,
    ) -> DiagnosisResult:
        if isinstance(evidence, (BuildEvidence, CommandEvidence)):
            command = evidence.command
            exit_code = evidence.exit_code
        else:
            command = None
            exit_code = None
        if isinstance(evidence, BuildEvidence):
            repair_attempt = evidence.repair_attempt
            max_repair_attempts = evidence.max_repair_attempts
        else:
            repair_attempt = None
            max_repair_attempts = None
        return result.model_copy(
            update={
                "report": FailureReport(
                    command=command,
                    exit_code=exit_code,
                    category=result.category,
                    evidence=result.evidence,
                    suggested_actions=result.suggested_actions,
                    repair_attempt=repair_attempt,
                    max_repair_attempts=max_repair_attempts,
                    proposed_diff=result.proposed_diff,
                )
            }
        )

    def _diagnose_build(self, evidence: BuildEvidence) -> DiagnosisResult:
        if evidence.exit_code == 0:
            return DiagnosisResult(category="build-succeeded")

        if evidence.repair_attempt >= evidence.max_repair_attempts:
            return DiagnosisResult(
                category="repair-limit-reached",
                evidence=[
                    f"repair attempts: {evidence.repair_attempt}/"
                    f"{evidence.max_repair_attempts}"
                ],
                suggested_actions=[
                    "stop automatic repair and preserve this failure evidence "
                    "for review"
                ],
            )
        package_match = re.search(
            r'Could not find a package configuration file provided by "([^"]+)"',
            evidence.stderr,
        )
        if package_match is None:
            package_match = re.search(
                r"package '([^']+)' not found",
                evidence.stderr,
            )
        if package_match is not None:
            package_name = package_match.group(1)
            apt_package = package_name.replace("_", "-")
            return DiagnosisResult(
                category="missing-ros-package",
                evidence=[package_name],
                suggested_actions=[
                    f"sudo apt install ros-jazzy-{apt_package}",
                    "source /opt/ros/jazzy/setup.bash and rebuild",
                ],
            )
        return DiagnosisResult(category="unknown-build-failure")

    def _diagnose_command(self, evidence: CommandEvidence) -> DiagnosisResult:
        if evidence.exit_code == 124:
            return DiagnosisResult(
                category="ros-command-timeout",
                evidence=[evidence.command],
                suggested_actions=[
                    "inspect controller_manager availability before retrying "
                    "ros2 control"
                ],
            )
        return DiagnosisResult(category="unknown-build-failure")

    def _diagnose_ros_graph(self, evidence: RosGraphEvidence) -> DiagnosisResult:
        if evidence.observed_message_type != evidence.required_message_type:
            return DiagnosisResult(
                category="topic-type-mismatch",
                evidence=[
                    f"{evidence.topic}: {evidence.observed_message_type} != "
                    f"{evidence.required_message_type}"
                ],
                suggested_actions=[
                    "add or configure a validated Twist-to-TwistStamped "
                    "conversion node"
                ],
            )
        return DiagnosisResult(category="unknown-build-failure")

    def _diagnose_tf(self, evidence: TfEvidence) -> DiagnosisResult:
        required_edge = (evidence.required_parent, evidence.required_child)
        if required_edge not in evidence.observed_edges:
            edge_text = f"{evidence.required_parent} -> {evidence.required_child}"
            return DiagnosisResult(
                category="missing-tf-transform",
                evidence=[f"missing transform: {edge_text}"],
                suggested_actions=[
                    f"start the node that publishes {edge_text} before navigation"
                ],
            )
        return DiagnosisResult(category="unknown-build-failure")

    def _diagnose_controllers(self, evidence: ControllerEvidence) -> DiagnosisResult:
        for controller in evidence.required_active:
            state = evidence.observed_states.get(controller, "missing")
            if state != "active":
                return DiagnosisResult(
                    category="inactive-controller",
                    evidence=[f"{controller}: {state}"],
                    suggested_actions=[
                        f"activate controller {controller} before commanding the robot"
                    ],
                )
        return DiagnosisResult(category="unknown-build-failure")

    def _diagnose_nodes(self, evidence: NodeEvidence) -> DiagnosisResult:
        for node in evidence.required_nodes:
            if node not in evidence.observed_nodes:
                return DiagnosisResult(
                    category="missing-ros-node",
                    evidence=[f"missing node: {node}"],
                    suggested_actions=[
                        f"start {node} before querying ros2 control"
                    ],
                )
        return DiagnosisResult(category="unknown-build-failure")

    def _diagnose_manifest(self, evidence: PackageManifestEvidence) -> DiagnosisResult:
        path = PurePosixPath(evidence.path)
        if (
            path.is_absolute()
            or ".." in path.parts
            or path.name != "package.xml"
            or "</package>" not in evidence.contents
        ):
            return DiagnosisResult(category="unknown-build-failure")
        dependency_line = f"  <depend>{evidence.missing_dependency}</depend>\n"
        updated_contents = evidence.contents.replace(
            "</package>",
            f"{dependency_line}</package>",
            1,
        )
        proposed_diff = "".join(
            difflib.unified_diff(
                evidence.contents.splitlines(keepends=True),
                updated_contents.splitlines(keepends=True),
                fromfile=evidence.path,
                tofile=evidence.path,
            )
        )
        return DiagnosisResult(
            category="missing-package-dependency",
            evidence=[f"{evidence.path}: {evidence.missing_dependency}"],
            suggested_actions=[
                "review the proposed package.xml dependency diff before applying"
            ],
            proposed_diff=proposed_diff,
        )
