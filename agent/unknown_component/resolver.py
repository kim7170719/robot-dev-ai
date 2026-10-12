"""Keep undocumented hardware blocked and documented hardware provisional."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier


class UnknownComponentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: Identifier
    documentation_sources: list[str] = Field(default_factory=list)


class UnknownComponentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["provisional", "blocked"]
    requires_human_approval: bool
    issues: list[str] = Field(default_factory=list)


class UnknownComponentResolver:
    def resolve(self, request: UnknownComponentRequest) -> UnknownComponentResult:
        if request.documentation_sources:
            return UnknownComponentResult(status="provisional", requires_human_approval=True)
        return UnknownComponentResult(
            status="blocked",
            requires_human_approval=False,
            issues=[f"unknown component has no documentation: {request.device_id}"],
        )
