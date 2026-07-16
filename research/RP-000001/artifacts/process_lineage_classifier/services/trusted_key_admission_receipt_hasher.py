import hashlib
import json
from collections import OrderedDict

from models import TrustedKeyAdmissionReceipt


class TrustedKeyAdmissionReceiptHashError(ValueError):
    """Raised when trusted-key admission receipt hashing fails."""


class TrustedKeyAdmissionReceiptHasher:
    """Canonicalizes, hashes, and validates admission receipts."""

    def canonicalize(
        self,
        receipt: TrustedKeyAdmissionReceipt,
    ) -> bytes:
        if not isinstance(
            receipt,
            TrustedKeyAdmissionReceipt,
        ):
            raise TypeError(
                "receipt must be a TrustedKeyAdmissionReceipt."
            )

        payload = OrderedDict(
            (
                ("receipt_id", receipt.receipt_id),
                ("registry_id", receipt.registry_id),
                (
                    "registry_version",
                    receipt.registry_version,
                ),
                (
                    "previous_registry_version",
                    receipt.previous_registry_version,
                ),
                ("snapshot_id", receipt.snapshot_id),
                ("snapshot_digest", receipt.snapshot_digest),
                ("material_id", receipt.material_id),
                ("key_id", receipt.key_id),
                (
                    "public_key_fingerprint",
                    receipt.public_key_fingerprint,
                ),
                ("owner_id", receipt.owner_id),
                ("issuer_id", receipt.issuer_id),
                ("admitted_by", receipt.admitted_by),
                (
                    "admission_reason",
                    receipt.admission_reason,
                ),
                (
                    "admitted_at",
                    receipt.admitted_at.isoformat(),
                ),
                ("admitted", receipt.admitted),
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
        receipt: TrustedKeyAdmissionReceipt,
    ) -> str:
        canonical = self.canonicalize(receipt)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        receipt: TrustedKeyAdmissionReceipt,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(receipt)

        if actual_digest != expected_digest:
            raise TrustedKeyAdmissionReceiptHashError(
                "Trusted-key admission receipt hash mismatch."
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
            raise TrustedKeyAdmissionReceiptHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise TrustedKeyAdmissionReceiptHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise TrustedKeyAdmissionReceiptHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )