from agent.mutation_safety import MutationRequest, MutationSafetyGate
from agent.hardware_readiness import ReadinessResult


def test_safety_permits_confirmed_mutation_after_readiness_and_rollback_are_present() -> None:
    result = MutationSafetyGate().evaluate(
        MutationRequest(
            mutation_id="add-lidar-config",
            diff="--- config.yaml\n+++ config.yaml\n+frame_id: lidar_link\n",
            rollback="restore the prior config.yaml",
            confirmed=True,
            readiness=ReadinessResult(ready=True, status="pass"),
        )
    )

    assert result.permitted is True
    assert result.status == "permitted"
    assert result.issues == []
