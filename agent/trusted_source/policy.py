"""Policy for classifying v0.5 discovery candidates without acquisition."""

from registry.v05 import SourceReview, TrustedSource


class TrustedSourcePolicy:
    """Classify metadata trust without cloning, downloading, or running a source."""

    def review(self, source: TrustedSource) -> SourceReview:
        if source.trust_level == "BLOCKED":
            return SourceReview(
                source_id=source.id,
                disposition="blocked",
                reasons=["source is explicitly blocked by the trust policy"],
            )
        if source.trust_level == "C":
            return SourceReview(
                source_id=source.id,
                disposition="sandbox-only",
                reasons=["community or personal sources require sandbox review"],
            )
        if source.license.redistribution == "unknown":
            return SourceReview(
                source_id=source.id,
                disposition="metadata-only",
                reasons=["license redistribution status must be reviewed before acquisition"],
            )
        return SourceReview(
            source_id=source.id,
            disposition="sandbox-only",
            reasons=[
                "metadata is traceable; any future acquisition remains sandbox-only",
                "human approval is required before promotion or deployment",
            ],
        )
