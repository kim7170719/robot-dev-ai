from agent.hardware_readiness import (
    HardwareReadinessGate,
    ReadinessCheck,
    ReadinessRequest,
)


def test_readiness_permits_only_when_all_required_checks_pass() -> None:
    result = HardwareReadinessGate().evaluate(
        ReadinessRequest(
            device_id="motor-controller",
            required_check_ids=["usb-present", "driver-installed", "emergency-stop"],
            checks=[
                ReadinessCheck(id="usb-present", status="pass", provenance="usb-inventory"),
                ReadinessCheck(
                    id="driver-installed", status="pass", provenance="package-query"
                ),
                ReadinessCheck(
                    id="emergency-stop", status="pass", provenance="manual-inspection"
                ),
            ],
        )
    )

    assert result.ready is True
    assert result.status == "pass"
    assert result.issues == []


def test_readiness_blocks_a_required_check_without_passing_evidence() -> None:
    result = HardwareReadinessGate().evaluate(
        ReadinessRequest(
            device_id="motor-controller",
            required_check_ids=["emergency-stop"],
            checks=[
                ReadinessCheck(
                    id="emergency-stop",
                    status="not-tested",
                    provenance="no-recorded-inspection",
                )
            ],
        )
    )

    assert result.ready is False
    assert result.status == "blocked"
    assert result.issues == ["readiness check emergency-stop: not-tested"]
