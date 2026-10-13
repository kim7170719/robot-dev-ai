from api.sandbox import sandbox_build_readiness_from_environment, sandbox_profile_from_environment


def test_docker_runner_is_not_configured_without_an_explicit_local_image(monkeypatch) -> None:
    monkeypatch.setenv("ROBOT_DEV_AI_SANDBOX_RUNNER", "docker")
    monkeypatch.delenv("ROBOT_DEV_AI_SANDBOX_IMAGE", raising=False)

    assert sandbox_profile_from_environment() is None


def test_docker_runner_profile_uses_only_the_explicit_image(monkeypatch) -> None:
    monkeypatch.setenv("ROBOT_DEV_AI_SANDBOX_RUNNER", "docker")
    monkeypatch.setenv("ROBOT_DEV_AI_SANDBOX_IMAGE", "local/sandbox:stable")

    profile = sandbox_profile_from_environment()

    assert profile is not None
    assert profile.image == "local/sandbox:stable"


def test_build_readiness_requires_an_explicit_local_build_image(monkeypatch) -> None:
    monkeypatch.delenv("ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE", raising=False)

    readiness = sandbox_build_readiness_from_environment()

    assert readiness.status == "not-configured"


def test_build_readiness_accepts_only_an_already_local_image(monkeypatch) -> None:
    monkeypatch.setenv("ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE", "local/ros-jazzy:stable")

    readiness = sandbox_build_readiness_from_environment(lambda image: image == "local/ros-jazzy:stable")

    assert readiness.status == "available"


def test_build_readiness_retains_an_immutable_local_image_identifier(monkeypatch) -> None:
    monkeypatch.setenv("ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE", "local/ros-jazzy:stable")

    readiness = sandbox_build_readiness_from_environment(
        lambda image: "sha256:" + "a" * 64
    )

    assert readiness.status == "available"
    assert readiness.image == "local/ros-jazzy:stable"
    assert readiness.image_id == "sha256:" + "a" * 64
