import hmac
from typing import Any

from services.historical_admissibility_evidence_trust_assessment_hasher import (
    HistoricalAdmissibilityEvidenceTrustAssessmentHasher,
)


_HEX_DIGITS = set("0123456789abcdef")


class HistoricalAdmissibilityEvidenceTrustAssessmentValidator:
    def __init__(self) -> None:
        self._hasher = (
            HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        )

    def validate(
        self,
        *,
        assessment: Any,
        expected_hash: str,
    ) -> bool:
        if assessment is None:
            raise ValueError("assessment is required")

        if not isinstance(expected_hash, str):
            raise ValueError("expected_hash must be a string")

        normalized_hash = expected_hash.strip().lower()

        if len(normalized_hash) != 64:
            raise ValueError(
                "expected_hash must contain exactly 64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_hash
        ):
            raise ValueError(
                "expected_hash must contain only hexadecimal characters"
            )

        actual_hash = self._hasher.hash_assessment(assessment)

        return hmac.compare_digest(
            actual_hash,
            normalized_hash,
        )