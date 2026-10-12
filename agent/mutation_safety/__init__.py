"""Safety decision boundary for proposed mutations; it never applies one."""

from .gate import MutationRequest, MutationResult, MutationSafetyGate

__all__ = ["MutationRequest", "MutationResult", "MutationSafetyGate"]
