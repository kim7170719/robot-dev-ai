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


def test_ros_manifest_metadata_reads_only_the_first_scanned_package_xml() -> None:
    observed: list[list[str]] = []

    def manifest_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        observed.append(command)
        if len(observed) == 1:
            return subprocess.CompletedProcess(
                command, 0, stdout="robot/package.xml\nother/package.xml\n", stderr=""
            )
        return subprocess.CompletedProcess(
            command, 0,
            stdout=("<package format=\"3\"><name>demo_robot</name><version>1.2.3</version>"
                    "<depend>rclpy</depend><exec_depend>sensor_msgs</exec_depend>"
                    "<depend>rclpy</depend></package>"),
            stderr="",
        )

    result = IsolatedSandboxRunner(manifest_runner).ros_manifest_metadata(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable"),
        Path("/safe/root/source.tar.gz"),
    )

    assert result.status == "passed"
    assert result.manifest_path == "robot/package.xml"
    assert result.package_name == "demo_robot"
    assert result.package_version == "1.2.3"
    assert result.dependency_ids == ["rclpy", "sensor_msgs"]
    assert observed[1][-1] == "robot/package.xml"
    assert "head -c 131073" in observed[1][-3]


def test_ros_manifest_metadata_command_preserves_docker_isolation_boundaries() -> None:
    command = IsolatedSandboxRunner.ros_manifest_metadata_command(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable"),
        Path("/safe/root/source.tar.gz"),
        "robot/package.xml",
    )

    assert command[:5] == ["docker", "run", "--rm", "--pull", "never"]
    assert ["--network", "none"] == command[command.index("--network") : command.index("--network") + 2]
    assert "--read-only" in command
    assert "dst=/bundle/source,readonly" in command[command.index("--mount") + 1]
    assert ["--cap-drop", "ALL"] == command[command.index("--cap-drop") : command.index("--cap-drop") + 2]


def test_ros_manifest_metadata_rejects_xml_declarations() -> None:
    calls = 0

    def declaration_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        stdout = "robot/package.xml\n" if calls == 1 else "<!DOCTYPE package [<!ENTITY a 'b'>]><package/>"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    result = IsolatedSandboxRunner(declaration_runner).ros_manifest_metadata(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable"),
        Path("/safe/root/source.tar.gz"),
    )

    assert result.status == "blocked"
    assert "declarations" in result.detail


def test_license_metadata_reads_only_the_first_scanned_license_declaration() -> None:
    calls = 0

    def license_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        stdout = "robot/LICENSE\nrobot/NOTICE\n" if calls == 1 else "SPDX-License-Identifier: Apache-2.0\n"
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    result = IsolatedSandboxRunner(license_runner).license_metadata(
        SandboxRunnerProfile(runner="docker", image="local/sandbox:stable"),
        Path("/safe/root/source.tar.gz"),
    )

    assert result.status == "passed"
    assert result.license_path == "robot/LICENSE"
    assert result.declared_spdx_expression == "Apache-2.0"
