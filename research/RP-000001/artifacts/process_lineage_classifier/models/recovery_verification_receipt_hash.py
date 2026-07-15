from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecoveryVerificationReceiptHash:
    """Immutable observer-only hash of a recovery verification receipt."""

    receipt_id: str
    algorithm: str
    digest: str
    canonical_payload: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.receipt_id, "receipt_id")
        self._require_non_empty(self.algorithm, "algorithm")
        self._require_non_empty(self.digest, "digest")
        self._require_non_empty(
            self.canonical_payload,
            "canonical_payload",
        )

        if self.algorithm != "sha256":
            from services.recovery_verification_receipt_hasher import (
                RecoveryVerificationReceiptHashingError,
            )

            raise RecoveryVerificationReceiptHashingError(
                "algorithm must be sha256."
            )

        expected_prefix = f"{self.algorithm}:"

        if not self.digest.startswith(expected_prefix):
            raise ValueError(
                "digest must include the configured algorithm prefix."
            )

        digest_value = self.digest.removeprefix(expected_prefix)

        if len(digest_value) != 64:
            raise ValueError(
                "sha256 digest must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise ValueError(
                "sha256 digest must contain only lowercase hexadecimal "
                "characters."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryVerificationReceiptHash must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryVerificationReceiptHash must not permit side effects."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be empty."
            )