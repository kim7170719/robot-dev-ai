"""A deliberately narrow, no-network self-test for the isolated runner."""

from __future__ import annotations

import subprocess
from typing import Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from .audit import SandboxRunnerPreflight, SandboxRunnerProfile


class SandboxSelfTestResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["passed", "blocked", "failed"]
    runner: str
    network_disabled: Literal[True] = True
    root_read_only: Literal[True] = True
    temporary_workspace: Literal[True] = True
    detail: str = Field(min_length=1, max_length=1024)


CommandRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


class IsolatedSandboxRunner:
    """Run only the fixed self-test; no caller-provided command is accepted."""

    def __init__(self, command_runner: CommandRunner | None = None) -> None:
        self.command_runner = command_runner or self._run_command

    @staticmethod
    def self_test_command(profile: SandboxRunnerProfile) -> list[str]:
        if profile.runner != "bubblewrap":
            raise ValueError("only bubblewrap is enabled for the first isolated self-test")
        return [
            "bwrap", "--die-with-parent", "--unshare-user", "--uid", "0", "--gid", "0",
            "--unshare-pid", "--unshare-net", "--new-session", "--ro-bind", "/", "/",
            "--tmpfs", "/tmp", "--proc", "/proc", "--dev", "/dev", "/bin/sh", "-c",
            "test ! -w /etc && test -w /tmp",
        ]

    def self_test(self, profile: SandboxRunnerProfile) -> SandboxSelfTestResult:
        readiness = SandboxRunnerPreflight().evaluate(profile)
        if readiness.status != "available":
            return SandboxSelfTestResult(
                status="blocked", runner=profile.runner,
                detail="; ".join(readiness.issues) or "sandbox runner is not ready",
            )
        if profile.runner != "bubblewrap":
            return SandboxSelfTestResult(
                status="blocked", runner=profile.runner,
                detail="Docker execution is not enabled in the first runner adapter",
            )
        try:
            completed = self.command_runner(self.self_test_command(profile))
        except (OSError, subprocess.TimeoutExpired) as error:
            return SandboxSelfTestResult(status="failed", runner=profile.runner, detail=str(error))
        if completed.returncode == 0:
            return SandboxSelfTestResult(
                status="passed", runner=profile.runner,
                detail="isolated self-test passed; no source was acquired or executed",
            )
        return SandboxSelfTestResult(
            status="failed", runner=profile.runner,
            detail=(completed.stderr or completed.stdout or "isolated self-test failed")[:1024],
        )

    @staticmethod
    def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
