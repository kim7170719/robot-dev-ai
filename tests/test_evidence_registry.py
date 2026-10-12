from agent.evidence_registry import EvidenceRegistry
from registry.models import RobotKnowledgeRegistry
from registry.v04 import RegistryDocumentV04
from registry.v06 import EvidenceEnvironment, EvidenceRecord, RegistryDocumentV06


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
