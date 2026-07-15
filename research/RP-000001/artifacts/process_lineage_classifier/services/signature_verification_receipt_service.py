from datetime import datetime

from models import SignatureVerificationReceipt


class SignatureVerificationReceiptError(ValueError):
    """Raised when a signature-verification receipt cannot be created."""


class SignatureVerificationReceiptService:
    """Creates verified observer-only signature-verification receipts."""

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
        verified_at: datetime,
        mathematical_verification: bool,
        identity_match: bool,
        content_match: bool,
        key_valid: bool,
    ) -> SignatureVerificationReceipt:
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
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            content_digest,
            "content_digest",
        )
        self._validate_digest(
            payload_digest,
            "payload_digest",
        )
        self._validate_digest(
            public_key_fingerprint,
            "public_key_fingerprint",
        )

        if algorithm != "ED25519":
            raise SignatureVerificationReceiptError(
                "algorithm must be ED25519."
            )

        self._validate_datetime(
            verified_at,
            "verified_at",
        )

        verification_components = (
            (
                "mathematical_verification",
                mathematical_verification,
            ),
            ("identity_match", identity_match),
            ("content_match", content_match),
            ("key_valid", key_valid),
        )

        for field_name, value in verification_components:
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        if not all(value for _, value in verification_components):
            raise SignatureVerificationReceiptError(
                "Every verification component must be true."
            )

        return SignatureVerificationReceipt(
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
            verified_at=verified_at,
            mathematical_verification=True,
            identity_match=True,
            content_match=True,
            key_valid=True,
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
            raise SignatureVerificationReceiptError(
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
            raise SignatureVerificationReceiptError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise SignatureVerificationReceiptError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise SignatureVerificationReceiptError(
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
            raise SignatureVerificationReceiptError(
                f"{field_name} must not be empty."
            )