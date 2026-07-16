import hmac
from typing import Any

from services.historical_admissibility_evidence_provenance_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceHasher,
)


_HEX_DIGITS = set("0123456789abcdef")


class HistoricalAdmissibilityEvidenceProvenanceValidator:
    def __init__(self) -> None:
        self._hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    def validate(
        self,
        *,
        provenance: Any,
        expected_hash: str,
    ) -> bool:
        if provenance is None:
            raise ValueError("provenance is required")

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

        actual_hash = self._hasher.hash_provenance(provenance)

        return hmac.compare_digest(
            actual_hash,
            normalized_hash,
        )