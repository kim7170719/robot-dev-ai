"""Context-aware evidence queries that preserve conflicting observations."""

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier
from registry.v06 import EvidenceRecord, RegistryDocumentV06


class EvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: Identifier
    records: list[EvidenceRecord] = Field(default_factory=list)
    coverage_levels: list[str] = Field(default_factory=list)
    conflict_record_ids: list[Identifier] = Field(default_factory=list)


class EvidenceRegistry:
    """Summarize a component's observations without collapsing their context."""

    def summarize(self, document: RegistryDocumentV06, component_id: Identifier) -> EvidenceSummary:
        records = sorted(
            (record for record in document.evidence_records if record.component_id == component_id),
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
        )
