from registry.models import RobotKnowledgeRegistry
from registry.v04 import RegistryDocumentV04
from registry.v06 import EvidenceEnvironment, EvidenceRecord, RegistryDocumentV06


def test_e3_simulation_evidence_is_environment_bound_without_real_robot_claim() -> None:
    registry = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {
                    "hardware": [
                        {"id": "diff-base", "kind": "mobile-base", "vendor": "Example"}
                    ]
                }
            ),
        ),
        evidence_records=[
            EvidenceRecord(
                id="diff-base-isaac-e3",
                component_id="diff-base",
                evidence_level="E3",
                source_trust="A",
                status="pass",
                environment=EvidenceEnvironment(
                    os="ubuntu-24-04", ros_distro="jazzy", cpu_arch="amd64"
                ),
                provenance="m4-navigation",
            )
        ],
    )

    record = registry.evidence_records[0]
    assert record.evidence_level == "E3"
    assert record.environment.cpu_arch == "amd64"
