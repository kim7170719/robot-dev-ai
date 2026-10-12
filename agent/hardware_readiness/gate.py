"""Evaluate recorded readiness facts; never inspect or control hardware."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier


ReadinessStatus = Literal["pass", "fail", "not-tested"]


class ReadinessCheck(BaseModel):
    """One attributable, externally collected readiness observation."""

    model_config = ConfigDict(extra="forbid")

    id: Identifier
    status: ReadinessStatus
    provenance: str = Field(min_length=1, max_length=128)


class ReadinessRequest(BaseModel):
    """Required checks and their recorded observations for one target device."""

    model_config = ConfigDict(extra="forbid")

    device_id: Identifier
    required_check_ids: list[Identifier] = Field(default_factory=list)
    checks: list[ReadinessCheck] = Field(default_factory=list)


class ReadinessResult(BaseModel):
    """A truthful permit/block decision with missing or failed evidence retained."""

    model_config = ConfigDict(extra="forbid")

    ready: bool
    status: Literal["pass", "blocked"]
    issues: list[str] = Field(default_factory=list)


class HardwareReadinessGate:
    """Block escalation unless every explicitly required check passed."""

    def evaluate(self, request: ReadinessRequest) -> ReadinessResult:
        observed = {check.id: check for check in request.checks}
        issues: list[str] = []
        for check_id in request.required_check_ids:
            check = observed.get(check_id)
            if check is None:
                issues.append(f"missing readiness check: {check_id}")
            elif check.status != "pass":
                issues.append(f"readiness check {check_id}: {check.status}")
        if issues:
            return ReadinessResult(ready=False, status="blocked", issues=issues)
        return ReadinessResult(ready=True, status="pass")
