"""Require readiness, reviewable diff, rollback, and confirmation before mutation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agent.hardware_readiness import ReadinessResult
from registry.models import Identifier


class MutationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mutation_id: Identifier
    diff: str = Field(min_length=1)
    rollback: str = Field(min_length=1)
    confirmed: bool = False
    readiness: ReadinessResult


class MutationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permitted: bool
    status: Literal["permitted", "blocked"]
    issues: list[str] = Field(default_factory=list)


class MutationSafetyGate:
    """Evaluate a proposal only; mutation application belongs outside this module."""

    def evaluate(self, request: MutationRequest) -> MutationResult:
        issues: list[str] = []
        if not request.readiness.ready:
            issues.append("hardware readiness is not passed")
        if not request.confirmed:
            issues.append("human confirmation is required")
        if issues:
            return MutationResult(permitted=False, status="blocked", issues=issues)
        return MutationResult(permitted=True, status="permitted")
