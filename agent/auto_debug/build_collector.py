"""Bounded collection of selected-package colcon build evidence."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from .diagnoser import BuildEvidence


BuildRunner = Callable[[tuple[str, ...], Path], BuildEvidence]
_PACKAGE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class BuildCommandCollector:
    """Run only colcon build --packages-select without a shell."""

    def __init__(
        self,
        workspace: Path,
        runner: BuildRunner | None = None,
    ) -> None:
        self._workspace = workspace
        self._runner = runner or _run_build

    def collect(self, packages: Sequence[str]) -> BuildEvidence:
        """Build explicitly named ROS packages and capture their evidence."""

        selected_packages = tuple(packages)
        if not selected_packages or any(
            _PACKAGE_NAME.fullmatch(package) is None
            for package in selected_packages
        ):
            raise ValueError("packages must be non-empty valid ROS package names")
        return self._runner(
            ("colcon", "build", "--packages-select", *selected_packages),
            self._workspace,
        )


def _run_build(arguments: tuple[str, ...], workspace: Path) -> BuildEvidence:
    try:
        completed = subprocess.run(
            arguments,
            cwd=workspace,
            check=False,
            capture_output=True,
            shell=False,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        return BuildEvidence(
            command=" ".join(arguments),
            exit_code=127,
            stderr="command not found: colcon",
        )
    except subprocess.TimeoutExpired:
        return BuildEvidence(
            command=" ".join(arguments),
            exit_code=124,
            stderr="build command timed out after 300 seconds",
        )
    return BuildEvidence(
        command=" ".join(arguments),
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
