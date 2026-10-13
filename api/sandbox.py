"""Environment-to-profile boundary for opt-in sandbox runner execution."""

import os

from agent.source_onboarding import SandboxRunnerProfile


def sandbox_profile_from_environment() -> SandboxRunnerProfile | None:
    runner = os.environ.get("ROBOT_DEV_AI_SANDBOX_RUNNER")
    if runner == "bubblewrap":
        return SandboxRunnerProfile(runner="bubblewrap")
    if runner == "docker":
        image = os.environ.get("ROBOT_DEV_AI_SANDBOX_IMAGE")
        if image:
            return SandboxRunnerProfile(runner="docker", image=image)
    return None
