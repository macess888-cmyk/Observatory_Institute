from datetime import datetime

from models import TrustedKeyAdmissionReceipt


class TrustedKeyAdmissionReceiptError(ValueError):
    """Raised when a trusted-key admission receipt cannot be created."""


class TrustedKeyAdmissionReceiptService:
    """Creates observer-only trusted-key admission receipts."""

    def create(
        self,
        *,
        receipt_id: str,
        registry_id: str,
        registry_version: str,
        previous_registry_version: str,
        snapshot_id: str,
        snapshot_digest: str,
        material_id: str,
        key_id: str,
        public_key_fingerprint: str,
        owner_id: str,
        issuer_id: str,
        admitted_by: str,
        admission_reason: str,
        admitted_at: datetime,
    ) -> TrustedKeyAdmissionReceipt:
        for field_name, value in (
            ("receipt_id", receipt_id),
            ("registry_id", registry_id),
            ("registry_version", registry_version),
            (
                "previous_registry_version",
                previous_registry_version,
            ),
            ("snapshot_id", snapshot_id),
            ("material_id", material_id),
            ("key_id", key_id),
            ("owner_id", owner_id),
            ("issuer_id", issuer_id),
            ("admitted_by", admitted_by),
            ("admission_reason", admission_reason),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            snapshot_digest,
            "snapshot_digest",
        )
        self._validate_digest(
            public_key_fingerprint,
            "public_key_fingerprint",
        )

        if registry_version == previous_registry_version:
            raise TrustedKeyAdmissionReceiptError(
                "registry version transition must change version."
            )

        self._validate_datetime(
            admitted_at,
            "admitted_at",
        )

        return TrustedKeyAdmissionReceipt(
            receipt_id=receipt_id,
            registry_id=registry_id,
            registry_version=registry_version,
            previous_registry_version=previous_registry_version,
            snapshot_id=snapshot_id,
            snapshot_digest=snapshot_digest,
            material_id=material_id,
            key_id=key_id,
            public_key_fingerprint=public_key_fingerprint,
            owner_id=owner_id,
            issuer_id=issuer_id,
            admitted_by=admitted_by,
            admission_reason=admission_reason,
            admitted_at=admitted_at,
            admitted=True,
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
            raise TrustedKeyAdmissionReceiptError(
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
            raise TrustedKeyAdmissionReceiptError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise TrustedKeyAdmissionReceiptError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise TrustedKeyAdmissionReceiptError(
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
            raise TrustedKeyAdmissionReceiptError(
                f"{field_name} must not be empty."
            )