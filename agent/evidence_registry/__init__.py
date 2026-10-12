"""Read-only evidence summaries for registry and presentation consumers."""

from .query import EvidenceRegistry, EvidenceSummary
from .snapshot import RegistrySnapshot

__all__ = ["EvidenceRegistry", "EvidenceSummary", "RegistrySnapshot"]
