from agent.trusted_source import TrustedSourcePolicy
from registry.models import RobotKnowledgeRegistry
from registry.v04 import RegistryDocumentV04
from registry.v05 import (
    ManagedComponent,
    RegistryManagementDocumentV05,
    SourceLicense,
    TrustedSource,
)
import pytest


def _source(*, trust_level: str = "A", redistribution: str = "allowed") -> TrustedSource:
    return TrustedSource(
        id="source-one",
        source_type="official-repo",
        url="https://example.test/repo",
        trust_level=trust_level,
        license=SourceLicense(spdx="MIT", redistribution=redistribution),
        retrieved_at="2026-10-12",
    )


def test_trusted_source_policy_never_authorizes_direct_acquisition() -> None:
    review = TrustedSourcePolicy().review(_source())

    assert review.disposition == "sandbox-only"
    assert "human approval" in review.reasons[1]


def test_blocked_source_cannot_enter_the_sandbox_path() -> None:
    review = TrustedSourcePolicy().review(_source(trust_level="BLOCKED"))

    assert review.disposition == "blocked"


def test_management_document_rejects_component_without_traceable_source() -> None:
    registry = RegistryDocumentV04(
        source_schema_version="v0.3",
        registry=RobotKnowledgeRegistry.model_validate(
            {"hardware": [{"id": "base", "kind": "mobile-base", "vendor": "Example"}]}
        ),
    )

    try:
        RegistryManagementDocumentV05(
            source_schema_version="v0.4",
            registry_v04=registry,
            sources=[_source()],
            components=[
                ManagedComponent(
                    id="base", kind="hardware", display_name="Base",
                    source_id="missing-source", lifecycle="discovered", provenance="test",
                )
            ],
        )
    except ValueError as error:
        assert "unknown source" in str(error)
    else:
        raise AssertionError("a component must retain a trusted source reference")


def test_trusted_source_requires_a_real_retrieval_date() -> None:
    with pytest.raises(ValueError):
        TrustedSource(
            id="source-invalid-date",
            source_type="official-repo",
            url="https://example.test/repo",
            trust_level="A",
            license=SourceLicense(spdx="MIT", redistribution="allowed"),
            retrieved_at="not-a-date",
        )
