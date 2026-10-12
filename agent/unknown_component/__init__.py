"""Safe classification of hardware absent from the registry."""

from .resolver import UnknownComponentRequest, UnknownComponentResolver, UnknownComponentResult

__all__ = ["UnknownComponentRequest", "UnknownComponentResolver", "UnknownComponentResult"]
