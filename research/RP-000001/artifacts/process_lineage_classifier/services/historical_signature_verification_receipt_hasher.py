import hashlib
import json
from collections import OrderedDict

from models import HistoricalSignatureVerificationReceipt


class HistoricalSignatureVerificationReceiptHashError(ValueError):
    """Raised when historical verification receipt hashing fails."""


class HistoricalSignatureVerificationReceiptHasher:
    """Canonicalizes, hashes, and validates historical verification receipts."""

    def canonicalize(
        self,
        receipt: HistoricalSignatureVerificationReceipt,
    ) -> bytes:
        if not isinstance(
            receipt,
            HistoricalSignatureVerificationReceipt,
        ):
            raise TypeError(
                "receipt must be a "
                "HistoricalSignatureVerificationReceipt."
            )

        payload = OrderedDict(
            (
                ("receipt_id", receipt.receipt_id),
                ("verification_id", receipt.verification_id),
                ("signature_id", receipt.signature_id),
                ("key_id", receipt.key_id),
                ("subject_id", receipt.subject_id),
                ("subject_type", receipt.subject_type),
                ("content_digest", receipt.content_digest),
                ("payload_digest", receipt.payload_digest),
                (
                    "public_key_fingerprint",
                    receipt.public_key_fingerprint,
                ),
                ("algorithm", receipt.algorithm),
                ("signer_id", receipt.signer_id),
                ("verifier_id", receipt.verifier_id),
                ("registry_id", receipt.registry_id),
                (
                    "signing_registry_version",
                    receipt.signing_registry_version,
                ),
                (
                    "signing_snapshot_id",
                    receipt.signing_snapshot_id,
                ),
                (
                    "signing_snapshot_digest",
                    receipt.signing_snapshot_digest,
                ),
                (
                    "verification_registry_version",
                    receipt.verification_registry_version,
                ),
                (
                    "verification_snapshot_id",
                    receipt.verification_snapshot_id,
                ),
                (
                    "verification_snapshot_digest",
                    receipt.verification_snapshot_digest,
                ),
                (
                    "signed_at",
                    receipt.signed_at.isoformat(),
                ),
                (
                    "verified_at",
                    receipt.verified_at.isoformat(),
                ),
                (
                    "mathematical_verification",
                    receipt.mathematical_verification,
                ),
                ("identity_match", receipt.identity_match),
                ("content_match", receipt.content_match),
                (
                    "signing_time_key_present",
                    receipt.signing_time_key_present,
                ),
                (
                    "verification_time_key_present",
                    receipt.verification_time_key_present,
                ),
                (
                    "key_valid_at_signing",
                    receipt.key_valid_at_signing,
                ),
                ("verified", receipt.verified),
                (
                    "execution_requested",
                    receipt.execution_requested,
                ),
                (
                    "side_effects_permitted",
                    receipt.side_effects_permitted,
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
        receipt: HistoricalSignatureVerificationReceipt,
    ) -> str:
        canonical = self.canonicalize(receipt)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        receipt: HistoricalSignatureVerificationReceipt,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(receipt)

        if actual_digest != expected_digest:
            raise HistoricalSignatureVerificationReceiptHashError(
                "Historical signature verification receipt "
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
            raise HistoricalSignatureVerificationReceiptHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise HistoricalSignatureVerificationReceiptHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise HistoricalSignatureVerificationReceiptHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )