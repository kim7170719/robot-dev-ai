"""A deliberately narrow, no-network self-test for the isolated runner."""

from __future__ import annotations

import subprocess
from pathlib import Path
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


class DependencyScanResult(BaseModel):
    """Archive listing evidence; no entry is extracted or executed."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["passed", "blocked", "failed"]
    runner: Literal["docker"]
    entry_count: int = Field(ge=0)
    top_level_entries: list[str] = Field(default_factory=list)
    candidate_dependency_manifests: list[str] = Field(default_factory=list)
    candidate_license_files: list[str] = Field(default_factory=list)
    detail: str = Field(min_length=1, max_length=1024)


CommandRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


class IsolatedSandboxRunner:
    """Run only the fixed self-test; no caller-provided command is accepted."""

    def __init__(self, command_runner: CommandRunner | None = None) -> None:
        self.command_runner = command_runner or self._run_command

    @staticmethod
    def self_test_command(profile: SandboxRunnerProfile) -> list[str]:
        if profile.runner == "docker":
            if profile.image is None:
                raise ValueError("Docker sandbox runner requires an explicitly configured local image")
            return [
                "docker", "run", "--rm", "--pull", "never", "--network", "none",
                "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
                "--pids-limit", "64", "--memory", "512m", "--cpus", "1",
                "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--user", "65534:65534", profile.image, "/bin/sh", "-c",
                "test ! -w /etc && test -w /tmp",
            ]
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
    def dependency_scan_command(profile: SandboxRunnerProfile, bundle_path: Path) -> list[str]:
        if profile.runner != "docker" or profile.image is None:
            raise ValueError("dependency scan requires a configured Docker sandbox profile")
        if not bundle_path.name.endswith((".tar.gz", ".tgz")):
            raise ValueError("dependency scan currently supports verified tar archives only")
        return [
            "docker", "run", "--rm", "--pull", "never", "--network", "none",
            "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
            "--pids-limit", "64", "--memory", "512m", "--cpus", "1",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--user", "65534:65534", "--mount",
            f"type=bind,src={bundle_path},dst=/bundle/source,readonly",
            profile.image, "/bin/sh", "-c", "tar -tzf /bundle/source",
        ]

    def dependency_scan(self, profile: SandboxRunnerProfile, bundle_path: Path) -> DependencyScanResult:
        readiness = SandboxRunnerPreflight().evaluate(profile)
        if readiness.status != "available":
            return DependencyScanResult(status="blocked", runner="docker", entry_count=0, detail="; ".join(readiness.issues))
        try:
            completed = self.command_runner(self.dependency_scan_command(profile, bundle_path))
        except (ValueError, OSError, subprocess.TimeoutExpired) as error:
            return DependencyScanResult(status="blocked", runner="docker", entry_count=0, detail=str(error))
        if completed.returncode != 0:
            return DependencyScanResult(status="failed", runner="docker", entry_count=0, detail=(completed.stderr or completed.stdout or "dependency scan failed")[:1024])
        entries = [line for line in completed.stdout.splitlines() if line][:4096]
        roots = sorted({entry.split("/", 1)[0] for entry in entries})[:64]
        manifests = [
            entry for entry in entries
            if entry.rsplit("/", 1)[-1] in {"package.xml", "package.json", "pyproject.toml", "requirements.txt"}
        ][:128]
        licenses = [
            entry for entry in entries
            if entry.rsplit("/", 1)[-1].upper().startswith(("LICENSE", "COPYING", "NOTICE"))
        ][:128]
        return DependencyScanResult(status="passed", runner="docker", entry_count=len(entries), top_level_entries=roots, candidate_dependency_manifests=manifests, candidate_license_files=licenses, detail="archive entries classified in an isolated read-only container; candidate metadata was not opened, extracted, or executed")

    @staticmethod
    def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
