import hashlib
import json
from collections import OrderedDict

from models import TrustedKeyRemovalReceipt


class TrustedKeyRemovalReceiptHashError(ValueError):
    """Raised when trusted-key removal receipt hashing fails."""


class TrustedKeyRemovalReceiptHasher:
    """Canonicalizes, hashes, and validates removal receipts."""

    def canonicalize(
        self,
        receipt: TrustedKeyRemovalReceipt,
    ) -> bytes:
        if not isinstance(
            receipt,
            TrustedKeyRemovalReceipt,
        ):
            raise TypeError(
                "receipt must be a TrustedKeyRemovalReceipt."
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
                (
                    "previous_snapshot_id",
                    receipt.previous_snapshot_id,
                ),
                (
                    "previous_snapshot_digest",
                    receipt.previous_snapshot_digest,
                ),
                (
                    "current_snapshot_id",
                    receipt.current_snapshot_id,
                ),
                (
                    "current_snapshot_digest",
                    receipt.current_snapshot_digest,
                ),
                ("material_id", receipt.material_id),
                ("key_id", receipt.key_id),
                (
                    "public_key_fingerprint",
                    receipt.public_key_fingerprint,
                ),
                ("owner_id", receipt.owner_id),
                ("issuer_id", receipt.issuer_id),
                ("removed_by", receipt.removed_by),
                (
                    "removal_reason",
                    receipt.removal_reason,
                ),
                (
                    "removed_at",
                    receipt.removed_at.isoformat(),
                ),
                ("removed", receipt.removed),
                (
                    "retroactive_invalidation",
                    receipt.retroactive_invalidation,
                ),
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
        receipt: TrustedKeyRemovalReceipt,
    ) -> str:
        canonical = self.canonicalize(receipt)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        receipt: TrustedKeyRemovalReceipt,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(receipt)

        if actual_digest != expected_digest:
            raise TrustedKeyRemovalReceiptHashError(
                "Trusted-key removal receipt hash mismatch."
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
            raise TrustedKeyRemovalReceiptHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise TrustedKeyRemovalReceiptHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise TrustedKeyRemovalReceiptHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )