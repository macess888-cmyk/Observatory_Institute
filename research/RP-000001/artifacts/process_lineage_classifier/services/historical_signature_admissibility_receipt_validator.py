import hmac
from typing import Any

from services.historical_signature_admissibility_receipt_hasher import (
    HistoricalSignatureAdmissibilityReceiptHasher,
)


_HEX_DIGITS = set("0123456789abcdef")


class HistoricalSignatureAdmissibilityReceiptValidator:
    def __init__(self) -> None:
        self._hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    def validate(
        self,
        *,
        receipt: Any,
        expected_hash: str,
    ) -> bool:
        if receipt is None:
            raise ValueError("receipt is required")

        if not isinstance(expected_hash, str):
            raise ValueError("expected_hash must be a string")

        normalized_hash = expected_hash.strip().lower()

        if len(normalized_hash) != 64:
            raise ValueError(
                "expected_hash must contain exactly 64 hexadecimal characters"
            )

        if any(character not in _HEX_DIGITS for character in normalized_hash):
            raise ValueError(
                "expected_hash must contain only hexadecimal characters"
            )

        actual_hash = self._hasher.hash_receipt(receipt)

        return hmac.compare_digest(
            actual_hash,
            normalized_hash,
        )