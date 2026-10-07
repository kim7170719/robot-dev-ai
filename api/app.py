"""Typed FastAPI boundary for the frozen Robot Dev AI core."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from agent.compatibility_resolver import (
    CompatibilityResolver,
    ResolutionRequest,
    ResolutionResult,
)
from agent.auto_debug.build_collector import BuildCommandCollector
from agent.auto_debug.collector import RosRuntimeCollector, RosRuntimeSnapshot
from agent.auto_debug.simulation_view import (
    CameraSource,
    SimulationFrame,
    SimulationFrameCollector,
)
from agent.auto_debug.diagnoser import (
    AutoDebugAgent,
    DiagnosisResult,
    PackageManifestEvidence,
)
from agent.mvp_pipeline import (
    IsaacScenario,
    IsaacSimulationValidator,
    MvpPipeline,
    MvpPipelineResult,
    SimulationValidationResult,
)
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


class SimulationValidationRequest(BaseModel):
    """Explicit confirmation for the one frozen virtual validation scenario."""

    model_config = ConfigDict(extra="forbid")

    confirmed: Literal[True]


class FullMvpRunRequest(BaseModel):
    """Explicitly run the frozen MVP pipeline in an ephemeral workspace."""

    model_config = ConfigDict(extra="forbid")

    natural_language: str = Field(min_length=1, max_length=10_000)
    confirmed: Literal[True]
    include_validation: bool = False


class FullMvpRunResult(BaseModel):
    """Evidence from one bounded full MVP run without retained artifacts."""

    model_config = ConfigDict(extra="forbid")

    pipeline: MvpPipelineResult
    runtime: RosRuntimeSnapshot
    validation: SimulationValidationResult | None = None
    workspace_lifecycle: Literal["ephemeral-cleaned"]


def create_app(
    project_summary: ProjectSummary | None = None,
    workspace_root: Path | None = None,
    build_collector_factory: Callable[[Path], BuildCommandCollector] | None = None,
    runtime_collector_factory: Callable[[], RosRuntimeCollector] | None = None,
    simulation_frame_collector_factory: Callable[[], SimulationFrameCollector] | None = None,
    simulation_validator_factory: Callable[[], IsaacSimulationValidator] | None = None,
    mvp_pipeline_factory: Callable[[Path], MvpPipeline] | None = None,
) -> FastAPI:
    """Create the presentation API without starting ROS or shell commands."""

    summary = project_summary or _default_project_summary()
    pending_plans: dict[str, WorkspacePlan] = {}
    generated_plans: dict[str, WorkspacePlan] = {}
    collector_factory = build_collector_factory or BuildCommandCollector
    snapshot_collector_factory = runtime_collector_factory or RosRuntimeCollector
    frame_collector_factory = (
        simulation_frame_collector_factory or SimulationFrameCollector
    )
    validator_factory = simulation_validator_factory or IsaacSimulationValidator
    pipeline_factory = mvp_pipeline_factory or _default_mvp_pipeline
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
        try:
            return TemplateExpander(template_root).expand(
                request.registry, request.request
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/api/v1/runtime/snapshot", response_model=RosRuntimeSnapshot)
    def read_runtime_snapshot() -> RosRuntimeSnapshot:
        return snapshot_collector_factory().collect_snapshot()

    @app.get("/api/v1/simulation/frame", response_model=SimulationFrame)
    def read_simulation_frame(source: CameraSource = "isaac") -> SimulationFrame:
        try:
            return frame_collector_factory().collect_frame(source)
        except RuntimeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @app.post(
        "/api/v1/validation/m4-navigation",
        response_model=SimulationValidationResult,
    )
    def validate_fixed_navigation(
        request: SimulationValidationRequest,
    ) -> SimulationValidationResult:
        return validator_factory().validate(IsaacScenario.M4_NAVIGATION)

    @app.post("/api/v1/mvp/full-run", response_model=FullMvpRunResult)
    def run_full_mvp(request: FullMvpRunRequest) -> FullMvpRunResult:
        with TemporaryDirectory(prefix="robot-dev-ai-mvp-") as directory:
            raw_pipeline = pipeline_factory(Path(directory)).run(request.natural_language)
            pipeline = raw_pipeline.model_copy(
                update={"generated_package_root": None}
            )
            runtime = snapshot_collector_factory().collect_snapshot()
            validation = None
            if request.include_validation and pipeline.status == "build-succeeded":
                validation = validator_factory().validate(IsaacScenario.M4_NAVIGATION)
        return FullMvpRunResult(
            pipeline=pipeline,
            runtime=runtime,
            validation=validation,
            workspace_lifecycle="ephemeral-cleaned",
        )

    @app.post("/api/v1/repairs/propose", response_model=DiagnosisResult)
    def propose_repair(evidence: PackageManifestEvidence) -> DiagnosisResult:
        return AutoDebugAgent().diagnose(evidence)

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

    gui_root = Path(__file__).parents[1] / "gui"
    app.mount("/", StaticFiles(directory=gui_root, html=True), name="gui")
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


def _default_mvp_pipeline(workspace_root: Path) -> MvpPipeline:
    """Compose the frozen four-capability MVP in a caller-owned temp workspace."""

    return MvpPipeline(
        registry=_frozen_mvp_registry(),
        hardware_id="generic-diff-base",
        template_root=Path(__file__).parents[1] / "templates",
        output_root=workspace_root / "src",
        build_collector=BuildCommandCollector(workspace_root),
    )


def _frozen_mvp_registry() -> RobotKnowledgeRegistry:
    """Return the validated registry used by the frozen M12 virtual MVP."""

    return RobotKnowledgeRegistry.model_validate(
        {
            "hardware": [
                {
                    "id": "generic-diff-base",
                    "kind": "mobile-base",
                    "vendor": "Robot Dev AI",
                    "capability_ids": [
                        "differential-drive",
                        "planar-lidar",
                        "rgb-camera",
                        "navigation",
                    ],
                }
            ],
            "drivers": [
                {
                    "id": "generic-diff-driver",
                    "hardware_id": "generic-diff-base",
                    "ros_distro": "jazzy",
                }
            ],
            "capabilities": [
                {
                    "id": "differential-drive",
                    "interface_ids": [],
                    "template_id": "differential-drive",
                },
                {
                    "id": "navigation",
                    "interface_ids": [],
                    "template_id": "nav2",
                },
                {
                    "id": "planar-lidar",
                    "interface_ids": [],
                    "template_id": "lidar",
                },
                {
                    "id": "rgb-camera",
                    "interface_ids": [],
                    "template_id": "camera",
                },
            ],
            "packages": [
                {
                    "id": "diff-drive-controller",
                    "required_capability_ids": ["differential-drive"],
                },
                {
                    "id": "nav2-bringup",
                    "required_capability_ids": ["navigation"],
                },
                {
                    "id": "lidar-driver",
                    "required_capability_ids": ["planar-lidar"],
                },
                {
                    "id": "camera-driver",
                    "required_capability_ids": ["rgb-camera"],
                },
            ],
            "compatibility": [
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "diff-drive-controller",
                    "status": "validated",
                },
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "nav2-bringup",
                    "status": "validated",
                },
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "lidar-driver",
                    "status": "validated",
                },
                {
                    "hardware_id": "generic-diff-base",
                    "package_id": "camera-driver",
                    "status": "validated",
                },
            ],
        }
    )
