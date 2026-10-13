import hashlib

from agent.source_onboarding import LocalSourceBundleGate, LocalSourceBundleRequest


def test_local_bundle_requires_matching_allowlisted_hash(tmp_path) -> None:
    bundle = tmp_path / "driver.tar.gz"
    bundle.write_bytes(b"local user supplied archive")
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    gate = LocalSourceBundleGate(tmp_path, {digest})

    result = gate.verify(LocalSourceBundleRequest(path=str(bundle), expected_sha256=digest))

    assert result.status == "verified"
    assert result.sha256 == digest


def test_verified_snapshot_is_read_only_and_not_the_mutable_source_path(tmp_path) -> None:
    bundle = tmp_path / "driver.tar.gz"
    bundle.write_bytes(b"reviewed source archive")
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    gate = LocalSourceBundleGate(tmp_path, {digest})

    with gate.verified_snapshot(
        LocalSourceBundleRequest(path=str(bundle), expected_sha256=digest)
    ) as snapshot:
        assert snapshot is not None
        assert snapshot != bundle
        assert snapshot.read_bytes() == bundle.read_bytes()
        assert snapshot.stat().st_mode & 0o222 == 0

    assert not snapshot.exists()


def test_local_bundle_rejects_path_outside_configured_root(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.tar.gz"
    outside.write_bytes(b"outside")
    digest = hashlib.sha256(outside.read_bytes()).hexdigest()

    result = LocalSourceBundleGate(root, {digest}).verify(
        LocalSourceBundleRequest(path=str(outside), expected_sha256=digest)
    )

    assert result.status == "blocked"
    assert "outside" in result.issues[0]


def test_local_bundle_rejects_symlink_even_when_it_resolves_inside_root(tmp_path) -> None:
    bundle = tmp_path / "real.tar.gz"
    bundle.write_bytes(b"real")
    alias = tmp_path / "alias.tar.gz"
    alias.symlink_to(bundle)
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()

    result = LocalSourceBundleGate(tmp_path, {digest}).verify(
        LocalSourceBundleRequest(path=str(alias), expected_sha256=digest)
    )

    assert result.status == "blocked"
    assert "symlink" in result.issues[0]


def test_verified_snapshot_rejects_a_source_path_replaced_with_a_symlink(tmp_path, monkeypatch) -> None:
    bundle = tmp_path / "driver.tar.gz"
    bundle.write_bytes(b"reviewed source archive")
    replacement = tmp_path / "replacement.tar.gz"
    replacement.write_bytes(b"replacement")
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    gate = LocalSourceBundleGate(tmp_path, {digest})
    verified = gate.verify

    def verify_then_replace(request: LocalSourceBundleRequest):
        result = verified(request)
        bundle.unlink()
        bundle.symlink_to(replacement)
        return result

    monkeypatch.setattr(gate, "verify", verify_then_replace)

    with gate.verified_snapshot(
        LocalSourceBundleRequest(path=str(bundle), expected_sha256=digest)
    ) as snapshot:
        assert snapshot is None
