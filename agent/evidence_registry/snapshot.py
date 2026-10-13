"""Immutable, content-addressed registry snapshots for reproducible benchmarks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from registry.v06 import RegistryDocumentV06


class RegistrySnapshot(BaseModel):
    """A copied document identified by its canonical serialized content."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    document: RegistryDocumentV06

    @classmethod
    def create(cls, document: RegistryDocumentV06) -> RegistrySnapshot:
        copied = RegistryDocumentV06.model_validate(document.model_dump(mode="json"))
        canonical = json.dumps(
            copied.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        return cls(
            id=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            document=copied,
        )


class RegistrySnapshotStore:
    """Retain content-addressed snapshots, optionally under a caller-owned directory."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._snapshots: dict[str, RegistrySnapshot] = {}

    def capture(self, document: RegistryDocumentV06) -> RegistrySnapshot:
        snapshot = RegistrySnapshot.create(document)
        self._snapshots.setdefault(snapshot.id, snapshot)
        if self.path is not None:
            self.path.mkdir(parents=True, exist_ok=True)
            target = self._path_for(snapshot.id)
            if target is not None:
                try:
                    with target.open("x", encoding="utf-8") as output:
                        output.write(snapshot.model_dump_json())
                except FileExistsError:
                    self._read_persisted(snapshot.id)
        return snapshot.model_copy(deep=True)

    def get(self, snapshot_id: str) -> RegistrySnapshot | None:
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot is None and self.path is not None:
            snapshot = self._read_persisted(snapshot_id)
            if snapshot is not None:
                self._snapshots[snapshot.id] = snapshot
        return snapshot.model_copy(deep=True) if snapshot is not None else None

    def _path_for(self, snapshot_id: str) -> Path | None:
        if not re.fullmatch(r"[a-f0-9]{64}", snapshot_id):
            return None
        return self.path / f"{snapshot_id}.json" if self.path is not None else None

    def _read_persisted(self, snapshot_id: str) -> RegistrySnapshot | None:
        target = self._path_for(snapshot_id)
        if target is None or not target.is_file():
            return None
        snapshot = RegistrySnapshot.model_validate_json(target.read_text(encoding="utf-8"))
        if snapshot.id != snapshot_id or RegistrySnapshot.create(snapshot.document).id != snapshot_id:
            raise ValueError("persisted registry snapshot content hash is invalid")
        return snapshot
