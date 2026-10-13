from agent.evidence_registry import RegistrySnapshot, RegistrySnapshotStore
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


def test_snapshot_store_retrieves_an_isolated_copy_by_content_id() -> None:
    document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {"hardware": [{"id": "diff-base", "kind": "mobile-base", "vendor": "Example"}]}
            ),
        ),
    )
    store = RegistrySnapshotStore()

    captured = store.capture(document)
    captured.document.registry_v04.registry.hardware[0].vendor = "Changed"
    restored = store.get(captured.id)

    assert restored is not None
    assert restored.document.registry_v04.registry.hardware[0].vendor == "Example"


def test_snapshot_store_recovers_a_verified_snapshot_from_caller_owned_storage(tmp_path) -> None:
    document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {"hardware": [{"id": "diff-base", "kind": "mobile-base", "vendor": "Example"}]}
            ),
        ),
    )
    first = RegistrySnapshotStore(tmp_path / "snapshots")
    captured = first.capture(document)

    restored = RegistrySnapshotStore(tmp_path / "snapshots").get(captured.id)

    assert restored == captured


def test_snapshot_store_rejects_tampered_persisted_content(tmp_path) -> None:
    document = RegistryDocumentV06(
        source_schema_version="v0.4",
        registry_v04=RegistryDocumentV04(
            source_schema_version="v0.3",
            registry=RobotKnowledgeRegistry.model_validate(
                {"hardware": [{"id": "diff-base", "kind": "mobile-base", "vendor": "Example"}]}
            ),
        ),
    )
    store = RegistrySnapshotStore(tmp_path / "snapshots")
    captured = store.capture(document)
    path = tmp_path / "snapshots" / f"{captured.id}.json"
    path.write_text(path.read_text(encoding="utf-8").replace("Example", "Tampered"), encoding="utf-8")

    import pytest
    with pytest.raises(ValueError, match="content hash"):
        RegistrySnapshotStore(tmp_path / "snapshots").get(captured.id)
