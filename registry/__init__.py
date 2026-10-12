"""Validated robot development knowledge records."""

from .v04 import (
    ArchitecturePlan,
    CompositionPlan,
    Constraint,
    HardwareProfileV04,
    RegistryDocumentV04,
    ResourceProfile,
    RobotSpecV04,
    SoftwareProfileV04,
    migrate_v03_registry,
)

__all__ = [
    "ArchitecturePlan",
    "CompositionPlan",
    "Constraint",
    "HardwareProfileV04",
    "RegistryDocumentV04",
    "ResourceProfile",
    "RobotSpecV04",
    "SoftwareProfileV04",
    "migrate_v03_registry",
]
