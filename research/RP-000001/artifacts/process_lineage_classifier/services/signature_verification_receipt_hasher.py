import hashlib
import json
from collections import OrderedDict

from models import SignatureVerificationReceipt


class SignatureVerificationReceiptHashError(ValueError):
    """Raised when signature-verification receipt hashing fails."""


class SignatureVerificationReceiptHasher:
    """Canonicalizes, hashes, and validates verification receipts."""

    def canonicalize(
        self,
        receipt: SignatureVerificationReceipt,
    ) -> bytes:
        if not isinstance(
            receipt,
            SignatureVerificationReceipt,
        ):
            raise TypeError(
                "receipt must be a SignatureVerificationReceipt."
            )

        payload = OrderedDict(
            (
                ("receipt_id", receipt.receipt_id),
                (
                    "verification_id",
                    receipt.verification_id,
                ),
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
                ("key_valid", receipt.key_valid),
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
        receipt: SignatureVerificationReceipt,
    ) -> str:
        canonical = self.canonicalize(receipt)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        receipt: SignatureVerificationReceipt,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(receipt)

        if actual_digest != expected_digest:
            raise SignatureVerificationReceiptHashError(
                "Signature-verification receipt hash mismatch."
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
            raise SignatureVerificationReceiptHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise SignatureVerificationReceiptHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise SignatureVerificationReceiptHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )