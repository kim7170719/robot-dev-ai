"""Read-only FastAPI boundary for the frozen Robot Dev AI core."""

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from agent.requirement_agent import RequirementAgent
from agent.schemas import RequirementResult


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


def create_app() -> FastAPI:
    """Create the read-only API without starting ROS or shell commands."""

    app = FastAPI(
        title="Robot Dev AI API",
        version="0.1.0",
        description="Typed presentation boundary for the frozen virtual MVP.",
    )

    @app.get("/api/v1/project/summary", response_model=ProjectSummary)
    def project_summary() -> ProjectSummary:
        return ProjectSummary(
            project_name="robot-dev-ai",
            branch="feature/m12-full-mvp",
            ros_distro="jazzy",
            isaac_sim_version="4.5.0",
            latest_passed_gate="G12",
            evidence_scope="virtual-only",
            cosmos_status="deferred",
        )

    @app.post("/api/v1/requirements/parse", response_model=RequirementResult)
    def parse_requirement(request: RequirementRequest) -> RequirementResult:
        return RequirementAgent().parse(request.natural_language)

    return app
