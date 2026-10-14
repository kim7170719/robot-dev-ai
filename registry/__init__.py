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
    CommunityEvidenceSubmission,
    EvidenceEnvironment,
    EvidenceRecord,
    RegistryDocumentV06,
    migrate_v04_registry,
)
from .v05 import (
    CompatibilityClaim,
    ManagedComponent,
    RegistryManagementDocumentV05,
    SourceLicense,
    SourceReview,
    TrustedSource,
)
from .g145 import (
    ComponentArtifact,
    SeedManifest,
    build_reference_registry,
    load_default_seed_manifest,
    load_seed_manifest,
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
    "CommunityEvidenceSubmission",
    "CompatibilityClaim",
    "ManagedComponent",
    "RegistryManagementDocumentV05",
    "SourceLicense",
    "SourceReview",
    "TrustedSource",
    "ComponentArtifact",
    "SeedManifest",
    "load_seed_manifest",
    "load_default_seed_manifest",
    "build_reference_registry",
]
