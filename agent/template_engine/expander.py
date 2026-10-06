"""Select and render a template authorized by a knowledge registry."""

from __future__ import annotations

from pathlib import Path
from string import Template

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier, RobotKnowledgeRegistry


class ExpansionRequest(BaseModel):
    """A request to render a template for one declared hardware capability."""

    model_config = ConfigDict(extra="forbid")

    hardware_id: Identifier
    capability_id: Identifier
    values: dict[str, str] = Field(default_factory=dict)


class ExpansionResult(BaseModel):
    """Rendered files, kept in memory for a caller to inspect or write."""

    model_config = ConfigDict(extra="forbid")

    template_id: Identifier
    files: dict[str, str]


class TemplateExpander:
    """Render only templates linked to capabilities declared by the hardware."""

    def __init__(self, template_root: Path) -> None:
        self._template_root = template_root

    def expand(
        self,
        registry: RobotKnowledgeRegistry,
        request: ExpansionRequest,
    ) -> ExpansionResult:
        hardware = next(
            (item for item in registry.hardware if item.id == request.hardware_id),
            None,
        )
        if hardware is None:
            raise ValueError(f"unknown hardware: {request.hardware_id}")
        if request.capability_id not in hardware.capability_ids:
            raise ValueError(
                f"hardware {request.hardware_id} does not declare capability "
                f"{request.capability_id}"
            )

        capability = next(
            (item for item in registry.capabilities if item.id == request.capability_id),
            None,
        )
        if capability is None:
            raise ValueError(f"unknown capability: {request.capability_id}")
        if capability.template_id is None:
            raise ValueError(f"capability {request.capability_id} has no template")

        source_root = self._template_root / capability.template_id
        source_files = sorted(source_root.rglob("*.template"))
        if not source_files:
            raise ValueError(f"template {capability.template_id} has no source files")

        rendered = {}
        for path in source_files:
            relative_path = Template(str(path.relative_to(source_root))).substitute(
                request.values
            )
            destination = str(Path(relative_path).with_suffix(""))
            rendered[destination] = Template(path.read_text(encoding="utf-8")).substitute(
                request.values
            )
        return ExpansionResult(template_id=capability.template_id, files=rendered)

    def write(self, result: ExpansionResult, output_root: Path) -> None:
        """Materialize a rendered result without allowing output-root escapes."""

        resolved_root = output_root.resolve()
        for relative_path, contents in result.files.items():
            target = resolved_root / relative_path
            resolved_target = target.resolve()
            if not resolved_target.is_relative_to(resolved_root):
                raise ValueError(f"template output escapes destination: {relative_path}")
            resolved_target.parent.mkdir(parents=True, exist_ok=True)
            resolved_target.write_text(contents, encoding="utf-8")
