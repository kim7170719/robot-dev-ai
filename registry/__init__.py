"""Validated robot development knowledge records."""

from .v04 import (
    ArchitecturePlan,
    CompositionPlan,
    HardwareProfileV04,
    RegistryDocumentV04,
    ResourceProfile,
    RobotSpecV04,
    migrate_v03_registry,
)

__all__ = [
    "ArchitecturePlan",
    "CompositionPlan",
    "HardwareProfileV04",
    "RegistryDocumentV04",
    "ResourceProfile",
    "RobotSpecV04",
    "migrate_v03_registry",
]
