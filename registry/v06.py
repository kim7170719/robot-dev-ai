"""Scalable, environment-bound evidence records layered over the v0.4 registry."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .models import Identifier, RegistryModel
from .v04 import EvidenceStatus, RegistryDocumentV04


EvidenceLevel = Literal["E0", "E1", "E2", "E3", "E4", "E5"]
SourceTrust = Literal["A", "B", "C", "blocked"]


class EvidenceEnvironment(RegistryModel):
    """The recorded execution context; evidence is never globally inferred."""

    os: str = Field(min_length=1, max_length=64)
    ros_distro: str = Field(min_length=1, max_length=32)
    cpu_arch: str = Field(min_length=1, max_length=32)


class EvidenceRecord(RegistryModel):
    """One immutable observation for a known component in one environment."""

    id: Identifier
    component_id: Identifier
    evidence_level: EvidenceLevel
    source_trust: SourceTrust
    status: EvidenceStatus
    environment: EvidenceEnvironment
    provenance: str = Field(min_length=1, max_length=128)


class RegistryDocumentV06(RegistryModel):
    """v0.6 envelope retaining v0.4 facts and appending contextual evidence."""

    schema_version: Literal["v0.6"] = "v0.6"
    source_schema_version: Literal["v0.4"]
    registry_v04: RegistryDocumentV04
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_references(self) -> RegistryDocumentV06:
        available = {
            hardware.id for hardware in self.registry_v04.registry.hardware
        } | {profile.id for profile in self.registry_v04.software_profiles} | {
            contract.id for contract in self.registry_v04.adapter_contracts
        }
        record_ids = [record.id for record in self.evidence_records]
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("v0.6 registry contains duplicate evidence identifiers")
        missing = sorted({record.component_id for record in self.evidence_records} - available)
        if missing:
            raise ValueError("evidence references unknown component: " + ", ".join(missing))
        return self


def migrate_v04_registry(document: RegistryDocumentV04) -> RegistryDocumentV06:
    """Wrap v0.4 facts without inventing E0–E5 evidence records."""

    return RegistryDocumentV06(source_schema_version="v0.4", registry_v04=document)
