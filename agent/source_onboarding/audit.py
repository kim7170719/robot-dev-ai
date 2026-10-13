"""Append-only audit records for source-onboarding decisions."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .transaction import OnboardingTransaction


class OnboardingAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    event: Literal["planned", "sandbox-runner-authorized", "bundle-verified", "blocked"]
    recorded_at: datetime
    detail: str = Field(min_length=1, max_length=512)


class OnboardingAuditStore:
    """A small append-only JSONL store; callers own its configured path."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.records: list[OnboardingAuditRecord] = []

    def append(
        self, transaction: OnboardingTransaction, event: Literal["planned", "sandbox-runner-authorized", "bundle-verified", "blocked"], detail: str
    ) -> OnboardingAuditRecord:
        record = OnboardingAuditRecord(
            transaction_id=transaction.id,
            event=event,
            recorded_at=datetime.now(UTC),
            detail=detail,
        )
        self.records.append(record)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as audit_file:
                audit_file.write(record.model_dump_json() + "\n")
        return record

    def has_event(self, transaction_id: str, event: str) -> bool:
        return any(
            record.transaction_id == transaction_id and record.event == event
            for record in self.records
        )


class OnboardingTransactionStore:
    """Recover preview transactions across API restarts from caller-owned JSONL."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.transactions: dict[str, OnboardingTransaction] = {}
        self._load()

    def _load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            transaction = OnboardingTransaction.model_validate_json(line)
            self.transactions[transaction.id] = transaction

    def save(self, transaction: OnboardingTransaction) -> None:
        self.transactions[transaction.id] = transaction
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as store_file:
                store_file.write(transaction.model_dump_json() + "\n")


class SandboxRunnerProfile(BaseModel):
    """The minimum isolation configuration a future runner must satisfy."""

    model_config = ConfigDict(extra="forbid")

    runner: Literal["bubblewrap", "docker"]
    image: str | None = Field(default=None, min_length=1, max_length=256)
    network_disabled: Literal[True] = True
    read_only_root: Literal[True] = True
    temporary_workspace: Literal[True] = True

    @model_validator(mode="after")
    def validate_docker_image(self) -> SandboxRunnerProfile:
        if self.runner == "docker" and self.image is None:
            raise ValueError("Docker sandbox runner requires an explicitly configured local image")
        return self


class SandboxRunnerReadiness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["available", "not-configured", "blocked"]
    runner: str | None = None
    issues: list[str] = Field(default_factory=list)


class SandboxRunnerPreflight:
    """Inspect runner availability only; never starts a container or namespace."""

    def evaluate(self, profile: SandboxRunnerProfile | None) -> SandboxRunnerReadiness:
        if profile is None:
            return SandboxRunnerReadiness(
                status="not-configured",
                issues=["no sandbox runner profile is configured"],
            )
        binary = "bwrap" if profile.runner == "bubblewrap" else "docker"
        if shutil.which(binary) is None:
            return SandboxRunnerReadiness(
                status="blocked", runner=profile.runner,
                issues=[f"configured sandbox runner is unavailable: {binary}"],
            )
        return SandboxRunnerReadiness(status="available", runner=profile.runner)


class SandboxAuthorizationResult(BaseModel):
    """Human confirmation authorizes handoff to a future sandbox runner only."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    status: Literal["sandbox-runner-authorized", "blocked"]
    host_execution_performed: Literal[False] = False
    audit_record: OnboardingAuditRecord


class SandboxExecutorContract:
    """Confirmation gate that records intent but never invokes a sandbox runner."""

    def authorize(
        self, transaction: OnboardingTransaction, *, confirmed: bool, audit_store: OnboardingAuditStore
    ) -> SandboxAuthorizationResult:
        if transaction.status == "blocked":
            record = audit_store.append(transaction, "blocked", "source policy blocks sandbox handoff")
            return SandboxAuthorizationResult(
                transaction_id=transaction.id, status="blocked", audit_record=record
            )
        if not confirmed:
            raise ValueError("human confirmation is required before sandbox handoff")
        record = audit_store.append(
            transaction,
            "sandbox-runner-authorized",
            "human confirmation recorded; no host execution was performed",
        )
        return SandboxAuthorizationResult(
            transaction_id=transaction.id,
            status="sandbox-runner-authorized",
            audit_record=record,
        )
