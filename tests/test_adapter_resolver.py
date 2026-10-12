from agent.adapter_resolver import AdapterResolutionRequest, AdapterResolver
from registry.models import RobotKnowledgeRegistry
from registry.v04 import (
    AdapterContract,
    Constraint,
    HardwareProfileV04,
    RegistryDocumentV04,
    SoftwareProfileV04,
)


def test_resolve_accepts_verified_serial_adapter_with_declared_facts() -> None:
    registry = RegistryDocumentV04(
        source_schema_version="v0.3",
        registry=RobotKnowledgeRegistry.model_validate(
            {
                "hardware": [
                    {
                        "id": "motor-controller",
                        "kind": "mobile-base",
                        "vendor": "Example",
                    }
                ]
            }
        ),
        software_profiles=[
            SoftwareProfileV04(
                id="serial-driver",
                kind="driver",
                version="1.0",
                verification_state="verified",
                provenance="test",
            )
        ],
        constraints=[
            Constraint(
                id="usb-serial",
                kind="transport",
                expected_value="USB serial",
                provenance="test",
            )
        ],
        hardware_profiles=[
            HardwareProfileV04(
                device_id="motor-controller",
                device_class="mobile-base",
                transport_ids=["usb-serial"],
                driver_ids=["serial-driver"],
                verification_state="verified",
                provenance="test",
            )
        ],
        adapter_contracts=[
            AdapterContract(
                id="serial-bridge",
                kind="serial",
                supported_device_classes=["mobile-base"],
                required_transport_ids=["usb-serial"],
                required_software_profile_ids=["serial-driver"],
                verification_state="verified",
                provenance="test",
            )
        ],
    )

    result = AdapterResolver().resolve(
        AdapterResolutionRequest(
            registry=registry,
            device_id="motor-controller",
            adapter_id="serial-bridge",
        )
    )

    assert result.ready is True
    assert result.issues == []
    assert result.adapter.id == "serial-bridge"
