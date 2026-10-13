"""Immutable, content-addressed registry snapshots for reproducible benchmarks."""

from __future__ import annotations

import hashlib
import json

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
    """Retain content-addressed, read-only snapshots for one application lifetime."""

    def __init__(self) -> None:
        self._snapshots: dict[str, RegistrySnapshot] = {}

    def capture(self, document: RegistryDocumentV06) -> RegistrySnapshot:
        snapshot = RegistrySnapshot.create(document)
        self._snapshots.setdefault(snapshot.id, snapshot)
        return snapshot.model_copy(deep=True)

    def get(self, snapshot_id: str) -> RegistrySnapshot | None:
        snapshot = self._snapshots.get(snapshot_id)
        return snapshot.model_copy(deep=True) if snapshot is not None else None
