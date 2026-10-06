from agent.requirement_agent import GeminiStructuredOutputProvider, RequirementAgent


class StubStructuredOutputProvider:
    def complete(
        self, natural_language: str, response_schema: dict[str, object]
    ) -> dict[str, object]:
        assert natural_language == "Build a differential-drive robot for Isaac Sim."
        assert "properties" in response_schema
        return {
            "specification": {
                "capability_ids": ["differential-drive"],
                "simulator": "isaac-sim",
            },
            "ambiguities": [],
            "provenance": {
                "capability_ids": "user",
                "simulator": "user",
            },
        }


class FakeGeminiInteractions:
    def __init__(self) -> None:
        self.request: dict[str, object] | None = None

    def create(self, **kwargs: object) -> object:
        self.request = kwargs
        return type(
            "Interaction",
            (),
            {
                "output_text": (
                    '{"specification":{"capability_ids":["differential-drive"],'
                    '"simulator":"isaac-sim"},"ambiguities":[],'
                    '"provenance":{"capability_ids":"user","simulator":"user"}}'
                )
            },
        )()


class FakeGeminiClient:
    def __init__(self) -> None:
        self.interactions = FakeGeminiInteractions()


def test_parse_uses_gemini_adapter_with_json_schema_response_format() -> None:
    client = FakeGeminiClient()
    provider = GeminiStructuredOutputProvider(api_key="test-key", client=client)

    result = RequirementAgent(provider=provider).parse(
        "Build a differential-drive robot for Isaac Sim."
    )

    assert result.specification.simulator == "isaac-sim"
    assert client.interactions.request is not None
    assert client.interactions.request["model"] == "gemini-3.5-flash-lite"
    assert client.interactions.request["response_format"]["mime_type"] == "application/json"


def test_parse_validates_structured_output_from_configured_provider() -> None:
    result = RequirementAgent(provider=StubStructuredOutputProvider()).parse(
        "Build a differential-drive robot for Isaac Sim."
    )

    assert result.specification.capability_ids == ["differential-drive"]
    assert result.specification.simulator == "isaac-sim"


class RetryingStructuredOutputProvider:
    def __init__(self) -> None:
        self.calls = 0

    def complete(
        self, natural_language: str, response_schema: dict[str, object]
    ) -> dict[str, object]:
        self.calls += 1
        if self.calls == 1:
            return {
                "specification": {
                    "capability_ids": ["lidar-2d"],
                    "simulator": "isaac-sim",
                }
            }
        return {
            "specification": {
                "capability_ids": ["differential-drive"],
                "simulator": "isaac-sim",
            },
            "ambiguities": [],
            "provenance": {"capability_ids": "user", "simulator": "user"},
        }


def test_parse_retries_provider_when_first_structured_output_is_invalid() -> None:
    provider = RetryingStructuredOutputProvider()

    result = RequirementAgent(provider=provider).parse("Build a robot.")

    assert provider.calls == 2
    assert result.specification.simulator == "isaac-sim"


def test_parse_explicit_mobile_robot_requirement_into_structured_spec() -> None:
    result = RequirementAgent().parse(
        "我要一台差速驅動機器人，具有 2D LiDAR、RGB 相機，使用 Nav2 並在 Isaac Sim 驗證"
    )

    assert result.specification.capability_ids == [
        "differential-drive",
        "planar-lidar",
        "rgb-camera",
        "navigation",
    ]
    assert result.specification.simulator == "isaac-sim"
    assert result.ambiguities == []
    assert result.provenance == {
        "capability_ids": "user",
        "simulator": "user",
    }


def test_parse_frozen_chinese_mvp_request_into_all_required_capabilities() -> None:
    result = RequirementAgent().parse(
        "我要建立一台 NVIDIA 差速機器車，LiDAR + Camera，能自主導航。"
    )

    assert result.specification.capability_ids == [
        "differential-drive",
        "planar-lidar",
        "rgb-camera",
        "navigation",
    ]
    assert result.ambiguities == []


def test_parse_reports_ambiguity_instead_of_inventing_capabilities() -> None:
    result = RequirementAgent().parse("請幫我做一台機器人")

    assert result.specification.capability_ids == []
    assert result.ambiguities == [
        "Specify at least one supported base, sensor, or navigation capability."
    ]
    assert result.provenance == {}
