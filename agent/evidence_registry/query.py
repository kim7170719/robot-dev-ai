"""Context-aware evidence queries that preserve conflicting observations."""

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier
from registry.v06 import EvidenceRecord, ReferenceRobot, RegistryDocumentV06


class EvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: Identifier
    records: list[EvidenceRecord] = Field(default_factory=list)
    coverage_levels: list[str] = Field(default_factory=list)
    conflict_record_ids: list[Identifier] = Field(default_factory=list)
    pending_community_submission_ids: list[Identifier] = Field(default_factory=list)


class EvidenceCoverageRow(BaseModel):
    """One component's visible evidence coverage without a synthetic roll-up."""

    model_config = ConfigDict(extra="forbid")

    component_id: Identifier
    coverage_levels: list[str] = Field(default_factory=list)
    record_count: int = Field(ge=0)
    conflict_record_ids: list[Identifier] = Field(default_factory=list)
    pending_community_submission_ids: list[Identifier] = Field(default_factory=list)


class EvidenceConflict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: Identifier
    record_ids: list[Identifier] = Field(min_length=2)


class EvidenceOverview(BaseModel):
    """Read-only overview for coverage, conflicts, and planned reference targets."""

    model_config = ConfigDict(extra="forbid")

    coverage_matrix: list[EvidenceCoverageRow] = Field(default_factory=list)
    conflicts: list[EvidenceConflict] = Field(default_factory=list)
    reference_robots: list[ReferenceRobot] = Field(default_factory=list)


class EvidenceRegistry:
    """Summarize a component's observations without collapsing their context."""

    def summarize(self, document: RegistryDocumentV06, component_id: Identifier) -> EvidenceSummary:
        records = sorted(
            (
                [record for record in document.evidence_records if record.component_id == component_id]
                + [
                    submission.record
                    for submission in document.community_submissions
                    if submission.record.component_id == component_id
                    and submission.review_state == "accepted"
                ]
            ),
            key=lambda record: record.id,
        )
        grouped: dict[tuple[str, str, str, str, str], set[str]] = {}
        for record in records:
            key = (
                record.evidence_level,
                record.environment.os,
                record.environment.ros_distro,
                record.environment.cpu_arch,
                record.source_trust,
            )
            grouped.setdefault(key, set()).add(record.status)
        conflicting_keys = {key for key, statuses in grouped.items() if {"pass", "fail"} <= statuses}
        conflicts = [
            record.id for record in records
            if (record.evidence_level, record.environment.os, record.environment.ros_distro,
                record.environment.cpu_arch, record.source_trust) in conflicting_keys
        ]
        return EvidenceSummary(
            component_id=component_id,
            records=records,
            coverage_levels=sorted({record.evidence_level for record in records}),
            conflict_record_ids=conflicts,
            pending_community_submission_ids=sorted(
                submission.id
                for submission in document.community_submissions
                if submission.record.component_id == component_id
                and submission.review_state == "pending-review"
            ),
        )

    def overview(self, document: RegistryDocumentV06) -> EvidenceOverview:
        """Show every known component and keep conflicts separately inspectable."""
        component_ids = sorted({
            hardware.id for hardware in document.registry_v04.registry.hardware
        } | {
            profile.id for profile in document.registry_v04.software_profiles
        } | {
            contract.id for contract in document.registry_v04.adapter_contracts
        })
        matrix = []
        conflicts = []
        for component_id in component_ids:
            summary = self.summarize(document, component_id)
            row = EvidenceCoverageRow(
                component_id=component_id,
                coverage_levels=summary.coverage_levels,
                record_count=len(summary.records),
                conflict_record_ids=summary.conflict_record_ids,
                pending_community_submission_ids=summary.pending_community_submission_ids,
            )
            matrix.append(row)
            if row.conflict_record_ids:
                conflicts.append(EvidenceConflict(
                    component_id=component_id, record_ids=row.conflict_record_ids
                ))
        return EvidenceOverview(
            coverage_matrix=matrix,
            conflicts=conflicts,
            reference_robots=sorted(document.reference_robots, key=lambda robot: robot.id),
        )
