import subprocess

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
