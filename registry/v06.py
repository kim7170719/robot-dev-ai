"""Scalable, environment-bound evidence records layered over the v0.4 registry."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .models import Identifier, RegistryModel
from .v04 import EvidenceStatus, RegistryDocumentV04


EvidenceLevel = Literal["E0", "E1", "E2", "E3", "E4", "E5"]
SourceTrust = Literal["A", "B", "C", "blocked"]
CommunityReviewState = Literal["pending-review", "accepted", "rejected"]
ReferenceRobotState = Literal["planned", "evidence-backed"]


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


class CommunityEvidenceSubmission(RegistryModel):
    """Unreviewed community evidence kept outside the accepted record set."""

    id: Identifier
    record: EvidenceRecord
    review_state: CommunityReviewState = "pending-review"
    submitted_by: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_community_submission(self) -> CommunityEvidenceSubmission:
        if self.record.source_trust != "C":
            raise ValueError("community submissions require source trust C")
        if self.record.evidence_level == "E5" and self.review_state != "accepted":
            raise ValueError("E5 community evidence requires accepted review")
        return self


class ReferenceRobot(RegistryModel):
    """A named composition target, never an implicit real-hardware claim."""

    id: Identifier
    display_name: str = Field(min_length=1, max_length=128)
    component_ids: list[Identifier] = Field(min_length=1)
    state: ReferenceRobotState = "planned"
    provenance: str = Field(min_length=1, max_length=128)


class RegistryDocumentV06(RegistryModel):
    """v0.6 envelope retaining v0.4 facts and appending contextual evidence."""

    schema_version: Literal["v0.6"] = "v0.6"
    source_schema_version: Literal["v0.4"]
    registry_v04: RegistryDocumentV04
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    community_submissions: list[CommunityEvidenceSubmission] = Field(default_factory=list)
    reference_robots: list[ReferenceRobot] = Field(default_factory=list)

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
        submission_ids = [submission.id for submission in self.community_submissions]
        if len(submission_ids) != len(set(submission_ids)):
            raise ValueError("v0.6 registry contains duplicate community submission identifiers")
        community_record_ids = [submission.record.id for submission in self.community_submissions]
        if len(record_ids + community_record_ids) != len(set(record_ids + community_record_ids)):
            raise ValueError("v0.6 registry contains duplicate evidence record identifiers")
        submission_components = {
            submission.record.component_id for submission in self.community_submissions
        }
        missing_submissions = sorted(submission_components - available)
        if missing_submissions:
            raise ValueError(
                "community submission references unknown component: "
                + ", ".join(missing_submissions)
            )
        accepted_e5_groups: dict[tuple[str, str, str, str, str], set[str]] = {}
        for submission in self.community_submissions:
            record = submission.record
            if record.evidence_level != "E5" or submission.review_state != "accepted":
                continue
            key = (
                record.component_id,
                record.status,
                record.environment.os,
                record.environment.ros_distro,
                record.environment.cpu_arch,
            )
            accepted_e5_groups.setdefault(key, set()).add(submission.submitted_by)
        if any(len(reviewers) < 2 for reviewers in accepted_e5_groups.values()):
            raise ValueError(
                "E5 community evidence requires two independent accepted submitters in one environment"
            )
        reference_ids = [reference.id for reference in self.reference_robots]
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("v0.6 registry contains duplicate reference robot identifiers")
        known_components = available | {
            profile.device_id for profile in self.registry_v04.hardware_profiles
        }
        missing_reference_components = sorted({
            component_id
            for reference in self.reference_robots
            for component_id in reference.component_ids
        } - known_components)
        if missing_reference_components:
            raise ValueError(
                "reference robot references unknown component: "
                + ", ".join(missing_reference_components)
            )
        return self


def migrate_v04_registry(document: RegistryDocumentV04) -> RegistryDocumentV06:
    """Wrap v0.4 facts without inventing E0–E5 evidence records."""

    return RegistryDocumentV06(source_schema_version="v0.4", registry_v04=document)
