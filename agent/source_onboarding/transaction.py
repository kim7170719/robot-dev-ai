"""Plan a source onboarding review without fetching, cloning, or executing it."""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agent.trusted_source import TrustedSourcePolicy
from registry.models import Identifier
from registry.v05 import ManagedComponent, SourceReview, TrustedSource


class OnboardingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component: ManagedComponent
    source: TrustedSource
    requested_by: str = Field(min_length=1, max_length=128)


class OnboardingTransaction(BaseModel):
    """Reviewable plan only; no field authorizes external execution."""

    model_config = ConfigDict(extra="forbid")

    id: Identifier
    status: Literal["blocked", "awaiting-human-confirmation"]
    component_id: Identifier
    source_review: SourceReview
    audit_diff: str
    sandbox_steps: list[Literal["isolated-acquisition", "dependency-scan", "build", "smoke-test", "ros-interface-validation"]] = Field(default_factory=list)
    execution_authorized: Literal[False] = False
    human_confirmation_required: Literal[True] = True


class SourceOnboardingPlanner:
    """Create deterministic onboarding plans while leaving execution unimplemented."""

    def preview(self, request: OnboardingRequest) -> OnboardingTransaction:
        if request.component.source_id != request.source.id:
            raise ValueError("onboarding component must reference its reviewed source")
        review = TrustedSourcePolicy().review(request.source)
        payload = request.model_dump(mode="json")
        transaction_id = "onboard-" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:16]
        audit_diff = (
            f"add {request.component.kind} {request.component.id} as {request.component.lifecycle}; "
            f"source={request.source.id}; requested_by={request.requested_by}"
        )
        if review.disposition == "blocked":
            return OnboardingTransaction(
                id=transaction_id,
                status="blocked",
                component_id=request.component.id,
                source_review=review,
                audit_diff=audit_diff,
            )
        return OnboardingTransaction(
            id=transaction_id,
            status="awaiting-human-confirmation",
            component_id=request.component.id,
            source_review=review,
            audit_diff=audit_diff,
            sandbox_steps=[
                "isolated-acquisition",
                "dependency-scan",
                "build",
                "smoke-test",
                "ros-interface-validation",
            ],
        )
