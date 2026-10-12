"""Resolve adapter contracts from recorded registry facts without hardware I/O."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from registry.models import Identifier
from registry.v04 import AdapterContract, RegistryDocumentV04


class AdapterResolutionRequest(BaseModel):
    """The explicitly requested adapter and physical device declaration."""

    model_config = ConfigDict(extra="forbid")

    registry: RegistryDocumentV04
    device_id: Identifier
    adapter_id: Identifier


class AdapterResolutionResult(BaseModel):
    """One compatible adapter contract or explicit missing-fact reasons."""

    model_config = ConfigDict(extra="forbid")

    ready: bool
    adapter: AdapterContract | None = None
    issues: list[str] = Field(default_factory=list)


class AdapterResolver:
    """Verify a selected adapter against declared device, driver, and transport facts."""

    def resolve(self, request: AdapterResolutionRequest) -> AdapterResolutionResult:
        profile = next(
            (
                profile
                for profile in request.registry.hardware_profiles
                if profile.device_id == request.device_id
            ),
            None,
        )
        if profile is None:
            return AdapterResolutionResult(
                ready=False,
                issues=[f"adapter resolution references unknown hardware profile: {request.device_id}"],
            )

        adapter = next(
            (
                adapter
                for adapter in request.registry.adapter_contracts
                if adapter.id == request.adapter_id
            ),
            None,
        )
        if adapter is None:
            return AdapterResolutionResult(
                ready=False,
                issues=[f"adapter resolution references unknown adapter contract: {request.adapter_id}"],
            )

        issues: list[str] = []
        if profile.device_class not in adapter.supported_device_classes:
            issues.append(
                f"adapter {adapter.id} does not support device class: {profile.device_class}"
            )
        missing_transports = sorted(
            set(adapter.required_transport_ids) - set(profile.transport_ids)
        )
        if missing_transports:
            issues.append(
                f"adapter {adapter.id} requires transports: {', '.join(missing_transports)}"
            )
        missing_software = sorted(
            set(adapter.required_software_profile_ids) - set(profile.driver_ids)
        )
        if missing_software:
            issues.append(
                f"adapter {adapter.id} requires software profiles: {', '.join(missing_software)}"
            )
        if adapter.verification_state == "unknown":
            issues.append(f"adapter {adapter.id} has unknown verification state")

        if issues:
            return AdapterResolutionResult(ready=False, issues=issues)
        return AdapterResolutionResult(ready=True, adapter=adapter)
