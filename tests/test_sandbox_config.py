from api.sandbox import sandbox_profile_from_environment


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
