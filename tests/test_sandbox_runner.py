import subprocess
from pathlib import Path

from agent.source_onboarding import IsolatedSandboxRunner, SandboxRunnerProfile


def test_bubblewrap_command_enforces_network_root_and_temp_boundaries() -> None:
    command = IsolatedSandboxRunner.self_test_command(SandboxRunnerProfile(runner="bubblewrap"))

    assert "--unshare-net" in command
    assert command[command.index("--ro-bind") + 1 : command.index("--ro-bind") + 3] == ["/", "/"]
    assert "--tmpfs" in command
    assert command[-1] == "test ! -w /etc && test -w /tmp"


def test_runner_passes_only_the_fixed_self_test_without_source_execution() -> None:
    observed: list[list[str]] = []

    def successful_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        observed.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = IsolatedSandboxRunner(successful_runner).self_test(
        SandboxRunnerProfile(runner="bubblewrap")
    )

    assert result.status == "passed"
    assert observed[0][-1] == "test ! -w /etc && test -w /tmp"


def test_docker_command_never_pulls_and_enforces_isolation_limits() -> None:
    command = IsolatedSandboxRunner.self_test_command(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable")
    )

    assert command[:5] == ["docker", "run", "--rm", "--pull", "never"]
    assert ["--network", "none"] == command[command.index("--network") : command.index("--network") + 2]
    assert "--read-only" in command
    assert ["--cap-drop", "ALL"] == command[command.index("--cap-drop") : command.index("--cap-drop") + 2]
    assert "local/sandbox:stable" in command


def test_dependency_scan_mounts_one_archive_read_only_without_extracting() -> None:
    command = IsolatedSandboxRunner.dependency_scan_command(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable"),
        Path("/safe/root/source.tar.gz"),
    )

    assert "--mount" in command
    assert "dst=/bundle/source,readonly" in command[command.index("--mount") + 1]
    assert command[-1] == "tar -tzf /bundle/source"


def test_dependency_scan_classifies_entry_name_candidates_without_opening_them() -> None:
    def listing_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="robot/package.xml\nrobot/LICENSE\nrobot/pyproject.toml\n", stderr="")

    result = IsolatedSandboxRunner(listing_runner).dependency_scan(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable"),
        Path("/safe/root/source.tar.gz"),
    )

    assert result.status == "passed"
    assert result.candidate_dependency_manifests == ["robot/package.xml", "robot/pyproject.toml"]
    assert result.candidate_license_files == ["robot/LICENSE"]
    assert "not opened" in result.detail
