import hashlib
import json
from collections import OrderedDict

from services.historical_signature_compromise_assessment import (
    HistoricalSignatureCompromiseAssessment,
)


class HistoricalSignatureCompromiseAssessmentHashError(ValueError):
    """Raised when compromise-assessment hashing fails."""


class HistoricalSignatureCompromiseAssessmentHasher:
    """Canonicalizes, hashes, and validates compromise assessments."""

    def canonicalize(
        self,
        assessment: HistoricalSignatureCompromiseAssessment,
    ) -> bytes:
        if not isinstance(
            assessment,
            HistoricalSignatureCompromiseAssessment,
        ):
            raise TypeError(
                "assessment must be a "
                "HistoricalSignatureCompromiseAssessment."
            )

        payload = OrderedDict(
            (
                ("assessment_id", assessment.assessment_id),
                ("receipt_id", assessment.receipt_id),
                ("verification_id", assessment.verification_id),
                ("signature_id", assessment.signature_id),
                ("key_id", assessment.key_id),
                ("material_id", assessment.material_id),
                (
                    "public_key_fingerprint",
                    assessment.public_key_fingerprint,
                ),
                (
                    "compromise_event_id",
                    assessment.compromise_event_id,
                ),
                (
                    "compromise_type",
                    assessment.compromise_type,
                ),
                (
                    "signed_at",
                    assessment.signed_at.isoformat(),
                ),
                (
                    "compromise_effective_at",
                    assessment.compromise_effective_at.isoformat(),
                ),
                (
                    "compromise_detected_at",
                    assessment.compromise_detected_at.isoformat(),
                ),
                (
                    "compromise_recorded_at",
                    assessment.compromise_recorded_at.isoformat(),
                ),
                (
                    "assessed_at",
                    assessment.assessed_at.isoformat(),
                ),
                ("assessed_by", assessment.assessed_by),
                (
                    "signature_precedes_compromise",
                    assessment.signature_precedes_compromise,
                ),
                (
                    "signature_at_or_after_compromise",
                    assessment.signature_at_or_after_compromise,
                ),
                (
                    "historical_validity_preserved",
                    assessment.historical_validity_preserved,
                ),
                (
                    "automatic_retroactive_invalidation",
                    assessment.automatic_retroactive_invalidation,
                ),
                ("status", assessment.status),
                (
                    "execution_requested",
                    assessment.execution_requested,
                ),
                (
                    "side_effects_permitted",
                    assessment.side_effects_permitted,
                ),
            )
        )

        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        return serialized.encode("utf-8")

    def hash(
        self,
        assessment: HistoricalSignatureCompromiseAssessment,
    ) -> str:
        canonical = self.canonicalize(assessment)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        assessment: HistoricalSignatureCompromiseAssessment,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(assessment)

        if actual_digest != expected_digest:
            raise HistoricalSignatureCompromiseAssessmentHashError(
                "Historical signature compromise assessment "
                "hash mismatch."
            )

        return True

    @staticmethod
    def _validate_digest(
        digest: str,
        field_name: str,
    ) -> None:
        if not isinstance(digest, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not digest.startswith(prefix):
            raise HistoricalSignatureCompromiseAssessmentHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise HistoricalSignatureCompromiseAssessmentHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise HistoricalSignatureCompromiseAssessmentHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )