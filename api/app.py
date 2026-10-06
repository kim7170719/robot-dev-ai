"""Read-only FastAPI boundary for the frozen Robot Dev AI core."""

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from agent.compatibility_resolver import (
    CompatibilityResolver,
    ResolutionRequest,
    ResolutionResult,
)
from agent.requirement_agent import RequirementAgent
from agent.schemas import RequirementResult
from registry.models import RobotKnowledgeRegistry


class ProjectSummary(BaseModel):
    """Stable project metadata rendered by the M14 dashboard."""

    model_config = ConfigDict(extra="forbid")

    project_name: str
    branch: str
    ros_distro: str
    isaac_sim_version: str
    latest_passed_gate: str
    evidence_scope: str
    cosmos_status: str


class RequirementRequest(BaseModel):
    """Natural-language input accepted by the Requirement view."""

    model_config = ConfigDict(extra="forbid")

    natural_language: str = Field(min_length=1, max_length=10_000)


class CompatibilityRequest(BaseModel):
    """Explicit registry and deployment context from Robot Configuration."""

    model_config = ConfigDict(extra="forbid")

    registry: RobotKnowledgeRegistry
    request: ResolutionRequest


def create_app(project_summary: ProjectSummary | None = None) -> FastAPI:
    """Create the read-only API without starting ROS or shell commands."""

    summary = project_summary or _default_project_summary()
    app = FastAPI(
        title="Robot Dev AI API",
        version="0.1.0",
        description="Typed presentation boundary for the frozen virtual MVP.",
    )

    @app.get("/api/v1/project/summary", response_model=ProjectSummary)
    def read_project_summary() -> ProjectSummary:
        return summary

    @app.post("/api/v1/requirements/parse", response_model=RequirementResult)
    def parse_requirement(request: RequirementRequest) -> RequirementResult:
        return RequirementAgent().parse(request.natural_language)

    @app.post("/api/v1/compatibility/resolve", response_model=ResolutionResult)
    def resolve_compatibility(request: CompatibilityRequest) -> ResolutionResult:
        return CompatibilityResolver().resolve(request.registry, request.request)

    return app


def _default_project_summary() -> ProjectSummary:
    """Read repository branch metadata without executing a Git command."""

    return ProjectSummary(
        project_name="robot-dev-ai",
        branch=_branch_from_head(Path(__file__).parents[1] / ".git" / "HEAD"),
        ros_distro="jazzy",
        isaac_sim_version="4.5.0",
        latest_passed_gate="G12",
        evidence_scope="virtual-only",
        cosmos_status="deferred",
    )


def _branch_from_head(head_path: Path) -> str:
    """Return the ref name in a standard Git worktree, or explicit unknown."""

    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"
    prefix = "ref: refs/heads/"
    return head.removeprefix(prefix) if head.startswith(prefix) else "detached"
