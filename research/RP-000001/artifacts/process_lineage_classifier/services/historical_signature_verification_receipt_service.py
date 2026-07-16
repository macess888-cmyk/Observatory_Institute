from datetime import datetime

from models import HistoricalSignatureVerificationReceipt


class HistoricalSignatureVerificationReceiptError(ValueError):
    """Raised when a historical verification receipt cannot be created."""


class HistoricalSignatureVerificationReceiptService:
    """Creates observer-only historical signature verification receipts."""

    def create(
        self,
        *,
        receipt_id: str,
        verification_id: str,
        signature_id: str,
        key_id: str,
        subject_id: str,
        subject_type: str,
        content_digest: str,
        payload_digest: str,
        public_key_fingerprint: str,
        algorithm: str,
        signer_id: str,
        verifier_id: str,
        registry_id: str,
        signing_registry_version: str,
        signing_snapshot_id: str,
        signing_snapshot_digest: str,
        verification_registry_version: str,
        verification_snapshot_id: str,
        verification_snapshot_digest: str,
        signed_at: datetime,
        verified_at: datetime,
        mathematical_verification: bool,
        identity_match: bool,
        content_match: bool,
        signing_time_key_present: bool,
        verification_time_key_present: bool,
        key_valid_at_signing: bool,
    ) -> HistoricalSignatureVerificationReceipt:
        for field_name, value in (
            ("receipt_id", receipt_id),
            ("verification_id", verification_id),
            ("signature_id", signature_id),
            ("key_id", key_id),
            ("subject_id", subject_id),
            ("subject_type", subject_type),
            ("algorithm", algorithm),
            ("signer_id", signer_id),
            ("verifier_id", verifier_id),
            ("registry_id", registry_id),
            (
                "signing_registry_version",
                signing_registry_version,
            ),
            (
                "signing_snapshot_id",
                signing_snapshot_id,
            ),
            (
                "verification_registry_version",
                verification_registry_version,
            ),
            (
                "verification_snapshot_id",
                verification_snapshot_id,
            ),
        ):
            self._require_non_empty(value, field_name)

        for field_name, value in (
            ("content_digest", content_digest),
            ("payload_digest", payload_digest),
            (
                "public_key_fingerprint",
                public_key_fingerprint,
            ),
            (
                "signing_snapshot_digest",
                signing_snapshot_digest,
            ),
            (
                "verification_snapshot_digest",
                verification_snapshot_digest,
            ),
        ):
            self._validate_digest(value, field_name)

        if algorithm != "ED25519":
            raise HistoricalSignatureVerificationReceiptError(
                "algorithm must be ED25519."
            )

        self._validate_datetime(
            signed_at,
            "signed_at",
        )
        self._validate_datetime(
            verified_at,
            "verified_at",
        )

        if verified_at < signed_at:
            raise HistoricalSignatureVerificationReceiptError(
                "Verification cannot occur before signature creation."
            )

        components = (
            (
                "mathematical_verification",
                mathematical_verification,
            ),
            ("identity_match", identity_match),
            ("content_match", content_match),
            (
                "signing_time_key_present",
                signing_time_key_present,
            ),
            (
                "verification_time_key_present",
                verification_time_key_present,
            ),
            (
                "key_valid_at_signing",
                key_valid_at_signing,
            ),
        )

        for field_name, value in components:
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        required_components = (
            mathematical_verification,
            identity_match,
            content_match,
            signing_time_key_present,
            key_valid_at_signing,
        )

        if not all(required_components):
            raise HistoricalSignatureVerificationReceiptError(
                "Every required verification component must be true."
            )

        return HistoricalSignatureVerificationReceipt(
            receipt_id=receipt_id,
            verification_id=verification_id,
            signature_id=signature_id,
            key_id=key_id,
            subject_id=subject_id,
            subject_type=subject_type,
            content_digest=content_digest,
            payload_digest=payload_digest,
            public_key_fingerprint=public_key_fingerprint,
            algorithm=algorithm,
            signer_id=signer_id,
            verifier_id=verifier_id,
            registry_id=registry_id,
            signing_registry_version=signing_registry_version,
            signing_snapshot_id=signing_snapshot_id,
            signing_snapshot_digest=signing_snapshot_digest,
            verification_registry_version=(
                verification_registry_version
            ),
            verification_snapshot_id=verification_snapshot_id,
            verification_snapshot_digest=(
                verification_snapshot_digest
            ),
            signed_at=signed_at,
            verified_at=verified_at,
            mathematical_verification=True,
            identity_match=True,
            content_match=True,
            signing_time_key_present=True,
            verification_time_key_present=(
                verification_time_key_present
            ),
            key_valid_at_signing=True,
            verified=True,
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
            raise HistoricalSignatureVerificationReceiptError(
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
            raise HistoricalSignatureVerificationReceiptError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise HistoricalSignatureVerificationReceiptError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise HistoricalSignatureVerificationReceiptError(
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
            raise HistoricalSignatureVerificationReceiptError(
                f"{field_name} must not be empty."
            )