import hashlib
import json
from collections import OrderedDict

from services.historical_signature_admissibility import (
    HistoricalSignatureAdmissibilityAssessment,
)


class HistoricalSignatureAdmissibilityAssessmentHashError(
    ValueError
):
    """Raised when admissibility-assessment hashing fails."""


class HistoricalSignatureAdmissibilityAssessmentHasher:
    """Canonicalizes, hashes, and validates admissibility assessments."""

    def canonicalize(
        self,
        assessment: HistoricalSignatureAdmissibilityAssessment,
    ) -> bytes:
        if not isinstance(
            assessment,
            HistoricalSignatureAdmissibilityAssessment,
        ):
            raise TypeError(
                "assessment must be a "
                "HistoricalSignatureAdmissibilityAssessment."
            )

        payload = OrderedDict(
            (
                (
                    "admissibility_id",
                    assessment.admissibility_id,
                ),
                ("receipt_id", assessment.receipt_id),
                (
                    "verification_id",
                    assessment.verification_id,
                ),
                ("signature_id", assessment.signature_id),
                ("key_id", assessment.key_id),
                (
                    "public_key_fingerprint",
                    assessment.public_key_fingerprint,
                ),
                (
                    "compromise_assessment_id",
                    assessment.compromise_assessment_id,
                ),
                (
                    "compromise_event_id",
                    assessment.compromise_event_id,
                ),
                ("assessed_by", assessment.assessed_by),
                (
                    "assessed_at",
                    assessment.assessed_at.isoformat(),
                ),
                (
                    "verification_evidence_available",
                    assessment.verification_evidence_available,
                ),
                (
                    "compromise_evidence_available",
                    assessment.compromise_evidence_available,
                ),
                (
                    "historical_validity_preserved",
                    assessment.historical_validity_preserved,
                ),
                ("outcome", assessment.outcome),
                ("admissible", assessment.admissible),
                (
                    "hold_required",
                    assessment.hold_required,
                ),
                ("rejected", assessment.rejected),
                (
                    "authorization_granted",
                    assessment.authorization_granted,
                ),
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
        assessment: HistoricalSignatureAdmissibilityAssessment,
    ) -> str:
        canonical = self.canonicalize(assessment)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        assessment: HistoricalSignatureAdmissibilityAssessment,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(assessment)

        if actual_digest != expected_digest:
            raise (
                HistoricalSignatureAdmissibilityAssessmentHashError(
                    "Historical signature admissibility "
                    "assessment hash mismatch."
                )
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
            raise (
                HistoricalSignatureAdmissibilityAssessmentHashError(
                    f"{field_name} must use the sha256 prefix."
                )
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise (
                HistoricalSignatureAdmissibilityAssessmentHashError(
                    f"{field_name} must contain "
                    "64 hexadecimal characters."
                )
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise (
                HistoricalSignatureAdmissibilityAssessmentHashError(
                    f"{field_name} must contain only lowercase "
                    "hexadecimal characters."
                )
            )