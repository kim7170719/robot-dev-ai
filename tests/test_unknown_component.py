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
