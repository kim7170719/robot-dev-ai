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
