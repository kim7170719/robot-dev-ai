from agent.source_onboarding import OnboardingRequest, SourceOnboardingPlanner
from agent.source_onboarding import OnboardingAuditStore, SandboxExecutorContract
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
