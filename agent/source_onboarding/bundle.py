"""Verify a user-supplied local source bundle before any sandbox handoff."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LocalSourceBundleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1, max_length=4096)
    expected_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class LocalSourceBundleVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["verified", "blocked"]
    filename: str
    sha256: str | None = None
    size_bytes: int | None = None
    issues: list[str] = Field(default_factory=list)


class LocalSourceBundleGate:
    """Reads only a regular, allowlisted archive under one configured root."""

    allowed_suffixes = (".tar.gz", ".tgz", ".zip")

    def __init__(self, root: Path | None, approved_hashes: set[str] | None = None, max_bytes: int = 512 * 1024 * 1024) -> None:
        self.root = root.resolve() if root is not None else None
        self.approved_hashes = approved_hashes or set()
        self.max_bytes = max_bytes

    def verify(self, request: LocalSourceBundleRequest) -> LocalSourceBundleVerification:
        filename = Path(request.path).name or "unknown"
        if self.root is None:
            return self._blocked(filename, "local source bundle root is not configured")
        candidate = Path(request.path)
        if candidate.is_symlink():
            return self._blocked(filename, "source bundle must not be a symlink")
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            return self._blocked(filename, "source bundle does not exist")
        if not resolved.is_relative_to(self.root):
            return self._blocked(filename, "source bundle is outside the configured root")
        if not resolved.is_file():
            return self._blocked(filename, "source bundle must be a regular non-symlink file")
        if not resolved.name.endswith(self.allowed_suffixes):
            return self._blocked(filename, "source bundle type is not allowlisted")
        size = resolved.stat().st_size
        if size > self.max_bytes:
            return self._blocked(filename, "source bundle exceeds the size limit")
        digest = self._sha256(resolved)
        if digest != request.expected_sha256:
            return self._blocked(filename, "source bundle hash differs from the supplied hash")
        if digest not in self.approved_hashes:
            return self._blocked(filename, "source bundle hash is not in the server allowlist")
        return LocalSourceBundleVerification(
            status="verified", filename=resolved.name, sha256=digest, size_bytes=size
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as bundle:
            for chunk in iter(lambda: bundle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def _blocked(filename: str, issue: str) -> LocalSourceBundleVerification:
        return LocalSourceBundleVerification(status="blocked", filename=filename, issues=[issue])
