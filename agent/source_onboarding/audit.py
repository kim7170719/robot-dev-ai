"""Append-only audit records for source-onboarding decisions."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .transaction import OnboardingTransaction


class OnboardingAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    event: Literal["planned", "sandbox-runner-authorized", "blocked"]
    recorded_at: datetime
    detail: str = Field(min_length=1, max_length=512)


class OnboardingAuditStore:
    """A small append-only JSONL store; callers own its configured path."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.records: list[OnboardingAuditRecord] = []

    def append(
        self, transaction: OnboardingTransaction, event: Literal["planned", "sandbox-runner-authorized", "blocked"], detail: str
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
