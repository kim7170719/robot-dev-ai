"""Environment-to-profile boundary for opt-in sandbox runner execution."""

import os
import shutil
import subprocess
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, Field

from agent.source_onboarding import SandboxRunnerProfile


class SandboxBuildReadiness(BaseModel):
    """Read-only preflight for a locally provisioned ROS build image."""

    model_config = ConfigDict(extra="forbid")

    status: str
    image: str | None = None
    image_id: str | None = None
    issues: list[str] = Field(default_factory=list)


def sandbox_profile_from_environment() -> SandboxRunnerProfile | None:
    runner = os.environ.get("ROBOT_DEV_AI_SANDBOX_RUNNER")
    if runner == "bubblewrap":
        return SandboxRunnerProfile(runner="bubblewrap")
    if runner == "docker":
        image = os.environ.get("ROBOT_DEV_AI_SANDBOX_IMAGE")
        if image:
            return SandboxRunnerProfile(runner="docker", image=image)
    return None


def sandbox_build_readiness_from_environment(
    image_inspector: Callable[[str], bool | str | None] | None = None,
) -> SandboxBuildReadiness:
    """Never pulls an image or starts a container; reports only local readiness."""
    image = os.environ.get("ROBOT_DEV_AI_SANDBOX_BUILD_IMAGE")
    if not image:
        return SandboxBuildReadiness(status="not-configured", issues=["no local ROS build image is configured"])
    if shutil.which("docker") is None:
        return SandboxBuildReadiness(status="blocked", image=image, issues=["configured Docker runner is unavailable"])
    inspector = image_inspector or _docker_image_identifier
    inspected = inspector(image)
    if not inspected:
        return SandboxBuildReadiness(status="blocked", image=image, issues=["configured ROS build image is not available locally"])
    return SandboxBuildReadiness(
        status="available", image=image,
        image_id=inspected if isinstance(inspected, str) else None,
    )


def _docker_image_identifier(image: str) -> str | None:
    try:
        completed = subprocess.run(
            ["docker", "image", "inspect", "--format", "{{.Id}}", image], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    identifier = completed.stdout.strip()
    return identifier if completed.returncode == 0 and identifier.startswith("sha256:") else None
