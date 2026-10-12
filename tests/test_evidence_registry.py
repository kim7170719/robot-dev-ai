from agent.evidence_registry import EvidenceRegistry
from registry.models import RobotKnowledgeRegistry
from registry.v04 import RegistryDocumentV04
from registry.v06 import EvidenceEnvironment, EvidenceRecord, RegistryDocumentV06
from registry.v06 import CommunityEvidenceSubmission


def test_summary_preserves_same_environment_pass_fail_conflict() -> None:
    environment = EvidenceEnvironment(os="ubuntu-24-04", ros_distro="jazzy", cpu_arch="amd64")
    document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {"hardware": [{"id": "ld06", "kind": "lidar", "vendor": "LDROBOT"}]}
            ),
        ),
        evidence_records=[
            EvidenceRecord(id="ld06-build-pass", component_id="ld06", evidence_level="E2", source_trust="A", status="pass", environment=environment, provenance="build-a"),
            EvidenceRecord(id="ld06-build-fail", component_id="ld06", evidence_level="E2", source_trust="A", status="fail", environment=environment, provenance="build-b"),
        ],
    )

    summary = EvidenceRegistry().summarize(document, "ld06")

    assert summary.coverage_levels == ["E2"]
    assert summary.conflict_record_ids == ["ld06-build-fail", "ld06-build-pass"]
    assert [record.id for record in summary.records] == ["ld06-build-fail", "ld06-build-pass"]


def test_pending_community_submission_is_visible_but_not_accepted_evidence() -> None:
    environment = EvidenceEnvironment(os="ubuntu-24-04", ros_distro="jazzy", cpu_arch="amd64")
    document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(source_schema_version="v0.3", registry=RobotKnowledgeRegistry.model_validate({"hardware": [{"id": "lidar", "kind": "lidar", "vendor": "Example"}]})),
        community_submissions=[
            CommunityEvidenceSubmission(
                id="lidar-community-e3", submitted_by="reviewer-a",
                record=EvidenceRecord(id="lidar-community-record", component_id="lidar", evidence_level="E3", source_trust="C", status="pass", environment=environment, provenance="community-report"),
            )
        ],
    )

    summary = EvidenceRegistry().summarize(document, "lidar")

    assert summary.records == []
    assert summary.pending_community_submission_ids == ["lidar-community-e3"]
