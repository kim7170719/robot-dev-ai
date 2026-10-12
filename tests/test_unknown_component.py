from agent.unknown_component import UnknownComponentRequest, UnknownComponentResolver


def test_documented_unknown_component_enters_provisional_human_approval_flow() -> None:
    result = UnknownComponentResolver().resolve(
        UnknownComponentRequest(
            device_id="custom-lidar",
            documentation_sources=["https://vendor.example/datasheet"],
        )
    )

    assert result.status == "provisional"
    assert result.requires_human_approval is True


def test_undocumented_unknown_component_is_blocked() -> None:
    result = UnknownComponentResolver().resolve(
        UnknownComponentRequest(device_id="custom-lidar")
    )

    assert result.status == "blocked"
    assert result.requires_human_approval is False
    assert result.issues == ["unknown component has no documentation: custom-lidar"]
