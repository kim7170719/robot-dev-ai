"""Constrained, workspace-local application of verified manifest repairs."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict

from .build_collector import BuildCommandCollector
from .diagnoser import AutoDebugAgent, DiagnosisResult, PackageManifestEvidence


class RepairResult(BaseModel):
    """Evidence from one bounded repair-and-rebuild attempt."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["repaired", "rejected", "build-failed"]
    reason: str | None = None
    build_diagnosis: DiagnosisResult | None = None


class ConstrainedRepairer:
    """Apply only an exact M11 package-manifest proposal inside one workspace."""

    def __init__(
        self,
        workspace_root: Path,
        build_collector: BuildCommandCollector,
    ) -> None:
        self._workspace_root = workspace_root.resolve()
        self._build_collector = build_collector

    def apply(self, proposal: DiagnosisResult) -> RepairResult:
        if (
            proposal.category != "missing-package-dependency"
            or proposal.proposed_diff is None
            or not proposal.evidence
        ):
            return RepairResult(status="rejected", reason="unsupported repair proposal")
        path, separator, dependency = proposal.evidence[0].partition(": ")
        relative = PurePosixPath(path)
        target = (self._workspace_root / relative).resolve()
        if (
            not separator
            or relative.is_absolute()
            or ".." in relative.parts
            or relative.name != "package.xml"
            or not target.is_relative_to(self._workspace_root / "src")
            or not target.is_file()
        ):
            return RepairResult(status="rejected", reason="manifest is outside workspace src")
        contents = target.read_text(encoding="utf-8")
        expected = AutoDebugAgent().diagnose(
            PackageManifestEvidence(
                path=path,
                contents=contents,
                missing_dependency=dependency,
            )
        )
        if expected.proposed_diff != proposal.proposed_diff:
            return RepairResult(status="rejected", reason="proposal does not match manifest")
        target.write_text(
            contents.replace(
                "</package>",
                f"  <depend>{dependency}</depend>\n</package>",
                1,
            ),
            encoding="utf-8",
        )
        package_match = re.search(r"<name>([^<]+)</name>", contents)
        if package_match is None:
            return RepairResult(status="rejected", reason="manifest has no package name")
        diagnosis = AutoDebugAgent().diagnose(
            self._build_collector.collect([package_match.group(1).strip()])
        )
        return RepairResult(
            status="repaired" if diagnosis.category == "build-succeeded" else "build-failed",
            build_diagnosis=diagnosis,
        )
