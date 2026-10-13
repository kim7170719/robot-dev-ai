from agent.source_onboarding import OnboardingRequest, SourceOnboardingPlanner
from agent.source_onboarding import (
    OnboardingAuditStore,
    OnboardingTransactionStore,
    SandboxExecutorContract,
    SandboxRunnerPreflight,
    SandboxRunnerProfile,
)
from registry.v05 import ManagedComponent, SourceLicense, TrustedSource


def _request(*, trust_level: str = "A") -> OnboardingRequest:
    source = TrustedSource(
        id="vendor-source", source_type="official-repo", url="https://example.test/source",
        trust_level=trust_level, license=SourceLicense(spdx="MIT", redistribution="allowed"),
        retrieved_at="2026-10-12",
    )
    return OnboardingRequest(
        component=ManagedComponent(id="new-lidar", kind="driver", display_name="New LiDAR Driver", source_id="vendor-source", lifecycle="discovered", provenance="operator-input"),
        source=source, requested_by="yu",
    )


def test_onboarding_preview_is_a_deterministic_nonexecuting_sandbox_plan() -> None:
    first = SourceOnboardingPlanner().preview(_request())
    second = SourceOnboardingPlanner().preview(_request())

    assert first.id == second.id
    assert first.status == "awaiting-human-confirmation"
    assert first.execution_authorized is False
    assert first.sandbox_steps == ["isolated-acquisition", "dependency-scan", "build", "smoke-test", "ros-interface-validation"]


def test_blocked_source_has_no_sandbox_steps() -> None:
    result = SourceOnboardingPlanner().preview(_request(trust_level="BLOCKED"))

    assert result.status == "blocked"
    assert result.sandbox_steps == []


def test_confirmed_handoff_persists_audit_without_host_execution(tmp_path) -> None:
    transaction = SourceOnboardingPlanner().preview(_request())
    store = OnboardingAuditStore(tmp_path / "audit.jsonl")

    result = SandboxExecutorContract().authorize(transaction, confirmed=True, audit_store=store)

    assert result.status == "sandbox-runner-authorized"
    assert result.host_execution_performed is False
    assert store.path.read_text(encoding="utf-8").count("sandbox-runner-authorized") == 1
    assert OnboardingAuditStore(store.path).records[0].record_hash is not None


def test_audit_store_rejects_a_tampered_hashed_record(tmp_path) -> None:
    transaction = SourceOnboardingPlanner().preview(_request())
    path = tmp_path / "audit.jsonl"
    SandboxExecutorContract().authorize(transaction, confirmed=True, audit_store=OnboardingAuditStore(path))
    path.write_text(path.read_text(encoding="utf-8").replace("human confirmation", "tampered confirmation"), encoding="utf-8")

    import pytest
    with pytest.raises(ValueError, match="hash chain"):
        OnboardingAuditStore(path)


def test_audit_store_chains_build_image_and_output_provenance(tmp_path) -> None:
    transaction = SourceOnboardingPlanner().preview(_request())
    path = tmp_path / "audit.jsonl"
    record = OnboardingAuditStore(path).append(
        transaction, "sandbox-build-passed", "isolated build passed",
        bundle_sha256="a" * 64, sandbox_image_ref="sha256:" + "b" * 64,
        output_sha256="c" * 64,
    )

    restored = OnboardingAuditStore(path).records[0]

    assert restored.record_hash == record.record_hash
    assert restored.sandbox_image_ref == "sha256:" + "b" * 64
    assert restored.output_sha256 == "c" * 64


def test_transaction_store_recovers_preview_across_a_new_store_instance(tmp_path) -> None:
    transaction = SourceOnboardingPlanner().preview(_request())
    path = tmp_path / "transactions.jsonl"
    OnboardingTransactionStore(path).save(transaction)

    restored = OnboardingTransactionStore(path)

    assert restored.transactions[transaction.id] == transaction


def test_sandbox_runner_preflight_is_not_configured_without_a_profile() -> None:
    result = SandboxRunnerPreflight().evaluate(None)

    assert result.status == "not-configured"
