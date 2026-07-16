from datetime import datetime

from models import TrustedKeyRemovalReceipt


class TrustedKeyRemovalReceiptError(ValueError):
    """Raised when a trusted-key removal receipt cannot be created."""


class TrustedKeyRemovalReceiptService:
    """Creates observer-only trusted-key removal receipts."""

    def create(
        self,
        *,
        receipt_id: str,
        registry_id: str,
        registry_version: str,
        previous_registry_version: str,
        previous_snapshot_id: str,
        previous_snapshot_digest: str,
        current_snapshot_id: str,
        current_snapshot_digest: str,
        material_id: str,
        key_id: str,
        public_key_fingerprint: str,
        owner_id: str,
        issuer_id: str,
        removed_by: str,
        removal_reason: str,
        removed_at: datetime,
        retroactive_invalidation: bool,
    ) -> TrustedKeyRemovalReceipt:
        for field_name, value in (
            ("receipt_id", receipt_id),
            ("registry_id", registry_id),
            ("registry_version", registry_version),
            (
                "previous_registry_version",
                previous_registry_version,
            ),
            (
                "previous_snapshot_id",
                previous_snapshot_id,
            ),
            (
                "current_snapshot_id",
                current_snapshot_id,
            ),
            ("material_id", material_id),
            ("key_id", key_id),
            ("owner_id", owner_id),
            ("issuer_id", issuer_id),
            ("removed_by", removed_by),
            ("removal_reason", removal_reason),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            previous_snapshot_digest,
            "previous_snapshot_digest",
        )
        self._validate_digest(
            current_snapshot_digest,
            "current_snapshot_digest",
        )
        self._validate_digest(
            public_key_fingerprint,
            "public_key_fingerprint",
        )

        if registry_version == previous_registry_version:
            raise TrustedKeyRemovalReceiptError(
                "registry version transition must change version."
            )

        if previous_snapshot_id == current_snapshot_id:
            raise TrustedKeyRemovalReceiptError(
                "snapshot transition must change snapshot identity."
            )

        if previous_snapshot_digest == current_snapshot_digest:
            raise TrustedKeyRemovalReceiptError(
                "snapshot digest transition must change digest."
            )

        self._validate_datetime(
            removed_at,
            "removed_at",
        )

        if not isinstance(retroactive_invalidation, bool):
            raise TypeError(
                "retroactive_invalidation must be a boolean."
            )

        if retroactive_invalidation is not False:
            raise TrustedKeyRemovalReceiptError(
                "Trusted-key removal must not claim "
                "retroactive invalidation."
            )

        return TrustedKeyRemovalReceipt(
            receipt_id=receipt_id,
            registry_id=registry_id,
            registry_version=registry_version,
            previous_registry_version=previous_registry_version,
            previous_snapshot_id=previous_snapshot_id,
            previous_snapshot_digest=previous_snapshot_digest,
            current_snapshot_id=current_snapshot_id,
            current_snapshot_digest=current_snapshot_digest,
            material_id=material_id,
            key_id=key_id,
            public_key_fingerprint=public_key_fingerprint,
            owner_id=owner_id,
            issuer_id=issuer_id,
            removed_by=removed_by,
            removal_reason=removal_reason,
            removed_at=removed_at,
            removed=True,
            retroactive_invalidation=False,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _validate_datetime(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(
                f"{field_name} must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise TrustedKeyRemovalReceiptError(
                f"{field_name} must be timezone-aware."
            )

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
            raise TrustedKeyRemovalReceiptError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise TrustedKeyRemovalReceiptError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise TrustedKeyRemovalReceiptError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
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
            raise TrustedKeyRemovalReceiptError(
                f"{field_name} must not be empty."
            )