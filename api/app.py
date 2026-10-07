"""Typed FastAPI boundary for the frozen Robot Dev AI core."""

from pathlib import Path
from typing import Callable, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from agent.compatibility_resolver import (
    CompatibilityResolver,
    ResolutionRequest,
    ResolutionResult,
)
from agent.auto_debug.build_collector import BuildCommandCollector
from agent.auto_debug.collector import RosRuntimeCollector, RosRuntimeSnapshot
from agent.auto_debug.diagnoser import AutoDebugAgent, DiagnosisResult
from agent.requirement_agent import RequirementAgent
from agent.schemas import RequirementResult
from agent.template_engine import ExpansionRequest, ExpansionResult, TemplateExpander
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


class TemplatePreviewRequest(BaseModel):
    """Registry-authorized template input rendered only in memory."""

    model_config = ConfigDict(extra="forbid")

    registry: RobotKnowledgeRegistry
    request: ExpansionRequest


class WorkspacePlanRequest(BaseModel):
    """A requested generated package below the configured workspace root."""

    model_config = ConfigDict(extra="forbid")

    output_name: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    registry: RobotKnowledgeRegistry
    requests: list[ExpansionRequest] = Field(min_length=1)


class WorkspacePlan(BaseModel):
    """A non-mutating preview that must be confirmed before generation."""

    model_config = ConfigDict(extra="forbid")

    confirmation_id: str
    status: Literal["awaiting-confirmation"]
    target_path: str
    files: dict[str, str]


class WorkspaceApplyRequest(BaseModel):
    """A second explicit confirmation for one pending workspace plan."""

    model_config = ConfigDict(extra="forbid")

    confirmation_id: str = Field(min_length=1)
    confirmed: Literal[True]


class WorkspaceApplyResult(BaseModel):
    """Evidence that a reviewed plan was materialized."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["generated"]
    target_path: str
    files: list[str]


class WorkspaceBuildRequest(BaseModel):
    """A third explicit confirmation to build one generated package."""

    model_config = ConfigDict(extra="forbid")

    confirmation_id: str = Field(min_length=1)
    confirmed: Literal[True]


class WorkspaceBuildResult(BaseModel):
    """Collected build evidence classified without applying a repair."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["build-succeeded", "build-failed"]
    diagnosis: DiagnosisResult


def create_app(
    project_summary: ProjectSummary | None = None,
    workspace_root: Path | None = None,
    build_collector_factory: Callable[[Path], BuildCommandCollector] | None = None,
    runtime_collector_factory: Callable[[], RosRuntimeCollector] | None = None,
) -> FastAPI:
    """Create the presentation API without starting ROS or shell commands."""

    summary = project_summary or _default_project_summary()
    pending_plans: dict[str, WorkspacePlan] = {}
    generated_plans: dict[str, WorkspacePlan] = {}
    collector_factory = build_collector_factory or BuildCommandCollector
    snapshot_collector_factory = runtime_collector_factory or RosRuntimeCollector
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

    @app.post("/api/v1/templates/preview", response_model=ExpansionResult)
    def preview_template(request: TemplatePreviewRequest) -> ExpansionResult:
        template_root = Path(__file__).parents[1] / "templates"
        return TemplateExpander(template_root).expand(request.registry, request.request)

    @app.get("/api/v1/runtime/snapshot", response_model=RosRuntimeSnapshot)
    def read_runtime_snapshot() -> RosRuntimeSnapshot:
        return snapshot_collector_factory().collect_snapshot()

    @app.post("/api/v1/workspaces/plan", response_model=WorkspacePlan)
    def plan_workspace(request: WorkspacePlanRequest) -> WorkspacePlan:
        if workspace_root is None:
            raise HTTPException(
                status_code=503, detail="workspace generation is not configured"
            )
        target = _workspace_target(workspace_root, request.output_name)
        if target.exists():
            raise HTTPException(status_code=409, detail="workspace target exists")
        expander = TemplateExpander(Path(__file__).parents[1] / "templates")
        files: dict[str, str] = {}
        try:
            for expansion_request in request.requests:
                result = expander.expand(request.registry, expansion_request)
                overlap = set(files).intersection(result.files)
                if overlap:
                    raise ValueError(
                        "multiple templates write the same file: "
                        + ", ".join(sorted(overlap))
                    )
                files.update(result.files)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        plan = WorkspacePlan(
            confirmation_id=uuid4().hex,
            status="awaiting-confirmation",
            target_path=str(target),
            files=files,
        )
        pending_plans[plan.confirmation_id] = plan
        return plan

    @app.post("/api/v1/workspaces/apply", response_model=WorkspaceApplyResult)
    def apply_workspace(request: WorkspaceApplyRequest) -> WorkspaceApplyResult:
        if workspace_root is None:
            raise HTTPException(
                status_code=503, detail="workspace generation is not configured"
            )
        plan = pending_plans.get(request.confirmation_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="workspace plan was not found")
        target = _workspace_target(workspace_root, Path(plan.target_path).name)
        if target.exists():
            raise HTTPException(status_code=409, detail="workspace target exists")
        TemplateExpander(Path(__file__).parents[1] / "templates").write(
            ExpansionResult(template_id="workspace", files=plan.files),
            target,
        )
        pending_plans.pop(plan.confirmation_id)
        generated_plans[plan.confirmation_id] = plan
        return WorkspaceApplyResult(
            status="generated",
            target_path=str(target),
            files=sorted(plan.files),
        )

    @app.post("/api/v1/workspaces/build", response_model=WorkspaceBuildResult)
    def build_workspace(request: WorkspaceBuildRequest) -> WorkspaceBuildResult:
        if workspace_root is None:
            raise HTTPException(
                status_code=503, detail="workspace generation is not configured"
            )
        plan = generated_plans.get(request.confirmation_id)
        if plan is None:
            raise HTTPException(
                status_code=404, detail="generated workspace plan was not found"
            )
        evidence = collector_factory(workspace_root).collect(
            [Path(plan.target_path).name]
        )
        diagnosis = AutoDebugAgent().diagnose(evidence)
        return WorkspaceBuildResult(
            status=(
                "build-succeeded"
                if diagnosis.category == "build-succeeded"
                else "build-failed"
            ),
            diagnosis=diagnosis,
        )

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


def _workspace_target(workspace_root: Path, output_name: str) -> Path:
    """Resolve a ROS package below the configured workspace's ``src`` directory."""

    root = workspace_root.resolve()
    source_root = (root / "src").resolve()
    target = (source_root / output_name).resolve()
    if not target.is_relative_to(source_root):
        raise HTTPException(status_code=422, detail="workspace target escapes root")
    return target
