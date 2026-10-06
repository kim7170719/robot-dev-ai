from pathlib import Path

from agent.auto_debug import (
    AutoDebugAgent,
    BuildCommandCollector,
    BuildEvidence,
    ConstrainedRepairer,
    PackageManifestEvidence,
)


def test_apply_repairs_only_proposed_manifest_then_rebuilds(tmp_path: Path) -> None:
    manifest = tmp_path / "src" / "demo_robot" / "package.xml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        '<package format="3">\n  <name>demo_robot</name>\n</package>\n',
        encoding="utf-8",
    )
    proposal = AutoDebugAgent().diagnose(
        PackageManifestEvidence(
            path="src/demo_robot/package.xml",
            contents=manifest.read_text(encoding="utf-8"),
            missing_dependency="geometry_msgs",
        )
    )
    observed: list[tuple[str, ...]] = []

    def runner(arguments: tuple[str, ...], workspace: Path) -> BuildEvidence:
        observed.append(arguments)
        assert workspace == tmp_path
        return BuildEvidence(command=" ".join(arguments), exit_code=0)

    result = ConstrainedRepairer(
        workspace_root=tmp_path,
        build_collector=BuildCommandCollector(tmp_path, runner=runner),
    ).apply(proposal)

    assert result.status == "repaired"
    assert "<depend>geometry_msgs</depend>" in manifest.read_text(encoding="utf-8")
    assert observed == [("colcon", "build", "--packages-select", "demo_robot")]
