from agent.evidence_registry import RegistrySnapshot
from registry.models import RobotKnowledgeRegistry
from registry.v04 import RegistryDocumentV04
from registry.v06 import RegistryDocumentV06


def test_snapshot_is_deterministic_and_retains_its_registry_copy() -> None:
    document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {"hardware": [{"id": "diff-base", "kind": "mobile-base", "vendor": "Example"}]}
            ),
        ),
    )

    first = RegistrySnapshot.create(document)
    second = RegistrySnapshot.create(document)

    assert first.id == second.id
    assert first.document == document
    assert len(first.id) == 64
