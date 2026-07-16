import hmac
from typing import Any

from services.historical_admissibility_evidence_package_hasher import (
    HistoricalAdmissibilityEvidencePackageHasher,
)


_HEX_DIGITS = set("0123456789abcdef")


class HistoricalAdmissibilityEvidencePackageValidator:
    def __init__(self) -> None:
        self._hasher = HistoricalAdmissibilityEvidencePackageHasher()

    def validate(
        self,
        *,
        package: Any,
        expected_hash: str,
    ) -> bool:
        if package is None:
            raise ValueError("package is required")

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

        actual_hash = self._hasher.hash_package(package)

        return hmac.compare_digest(
            actual_hash,
            normalized_hash,
        )