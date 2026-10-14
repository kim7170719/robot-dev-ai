from pathlib import Path

import pytest

from registry.g145 import SeedManifest, load_seed_manifest


def test_p0_seed_manifest_is_loadable_and_preserves_evidence_boundaries() -> None:
    manifest = load_seed_manifest(
        Path(__file__).parents[1] / "data" / "registry" / "seed_manifest.yaml"
    )

    assert manifest.schema_version == "g14.5"
    assert [artifact.id for artifact in manifest.artifacts] == [
        "differential-drive", "jetson-generic", "esp32", "serial-bridge",
        "ros2-control", "diff-drive-controller", "ld06", "realsense-d455",
        "nav2", "isaac-sim", "twist-twiststamped",
    ]
    assert all(artifact.verification.evidence_level not in {"E4", "E5"} for artifact in manifest.artifacts)
    assert all(artifact.source.url.startswith("https://") for artifact in manifest.artifacts)


def test_seed_manifest_rejects_real_hardware_claims() -> None:
    payload = {
        "artifacts": [{
            "id": "invalid-e4", "name": "Invalid", "artifact_type": "hardware_profile",
            "vendor": "Example", "model": "Example", "source": {
                "source_type": "official-repo", "url": "https://example.test/repo",
                "trust_level": "A", "license": {"spdx": "MIT", "redistribution": "allowed"},
                "retrieved_at": "2026-10-14",
            },
            "verification": {"evidence_level": "E4", "status": "pass", "target_evidence_level": "E4"},
            "provenance": "test",
        }],
    }

    with pytest.raises(ValueError, match="cannot claim E4 or E5"):
        SeedManifest.model_validate(payload)
