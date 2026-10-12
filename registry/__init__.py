"""Validated robot development knowledge records."""

from .v04 import (
    AdapterContract,
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
from .v06 import (
    EvidenceEnvironment,
    EvidenceRecord,
    RegistryDocumentV06,
    migrate_v04_registry,
)

__all__ = [
    "AdapterContract",
    "ArchitecturePlan",
    "CompositionPlan",
    "Constraint",
    "HardwareProfileV04",
    "RegistryDocumentV04",
    "ResourceProfile",
    "RobotSpecV04",
    "SoftwareProfileV04",
    "migrate_v03_registry",
    "EvidenceEnvironment",
    "EvidenceRecord",
    "RegistryDocumentV06",
    "migrate_v04_registry",
]
