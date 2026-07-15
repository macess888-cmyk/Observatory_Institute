from datetime import datetime

from models import (
    DetachedSignature,
    SignatureVerification,
    SigningKeyIdentity,
)


class SignatureVerificationError(ValueError):
    """Raised when a detached signature cannot be verified."""


class SignatureVerificationService:
    """Verifies signature references, key validity, and identity alignment."""

    def verify(
        self,
        *,
        verification_id: str,
        signature: DetachedSignature,
        key: SigningKeyIdentity,
        expected_subject_id: str,
        expected_subject_type: str,
        expected_content_digest: str,
        verified_at: datetime,
        verifier_id: str,
    ) -> SignatureVerification:
        if not isinstance(signature, DetachedSignature):
            raise TypeError(
                "signature must be a DetachedSignature."
            )

        if not isinstance(key, SigningKeyIdentity):
            raise TypeError(
                "key must be a SigningKeyIdentity."
            )

        self._require_non_empty(
            verification_id,
            "verification_id",
        )
        self._require_non_empty(
            expected_subject_id,
            "expected_subject_id",
        )
        self._require_non_empty(
            expected_subject_type,
            "expected_subject_type",
        )
        self._validate_digest(
            expected_content_digest,
            "expected_content_digest",
        )
        self._require_non_empty(
            verifier_id,
            "verifier_id",
        )
        self._validate_verification_time(
            verified_at,
            signature=signature,
        )

        self._validate_key_and_signature(
            signature=signature,
            key=key,
        )
        self._validate_subject_and_content(
            signature=signature,
            expected_subject_id=expected_subject_id,
            expected_subject_type=expected_subject_type,
            expected_content_digest=expected_content_digest,
        )

        return SignatureVerification(
            verification_id=verification_id,
            signature_id=signature.signature_id,
            key_id=key.key_id,
            subject_id=signature.subject_id,
            subject_type=signature.subject_type,
            content_digest=signature.content_digest,
            signer_id=signature.signer_id,
            key_owner_id=key.owner_id,
            algorithm=signature.algorithm,
            signature_verified=True,
            key_valid=True,
            identity_match=True,
            content_match=True,
            verified=True,
            verified_at=verified_at,
            verifier_id=verifier_id,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _validate_key_and_signature(
        *,
        signature: DetachedSignature,
        key: SigningKeyIdentity,
    ) -> None:
        if signature.key_id != key.key_id:
            raise SignatureVerificationError(
                "Signature contains a key identity mismatch."
            )

        if signature.signer_id != key.owner_id:
            raise SignatureVerificationError(
                "Signature contains a signer identity mismatch."
            )

        if signature.algorithm != key.algorithm:
            raise SignatureVerificationError(
                "Signature and signing key contain an algorithm mismatch."
            )

        if key.revoked:
            raise SignatureVerificationError(
                "Signing key has been revoked."
            )

        if signature.signed_at < key.valid_from:
            raise SignatureVerificationError(
                "Signature was created before key validity began."
            )

        if signature.signed_at > key.valid_until:
            raise SignatureVerificationError(
                "Signature was created after key validity ended."
            )

    @staticmethod
    def _validate_subject_and_content(
        *,
        signature: DetachedSignature,
        expected_subject_id: str,
        expected_subject_type: str,
        expected_content_digest: str,
    ) -> None:
        if signature.subject_id != expected_subject_id:
            raise SignatureVerificationError(
                "Signature contains a subject identity mismatch."
            )

        if signature.subject_type != expected_subject_type:
            raise SignatureVerificationError(
                "Signature contains a subject type mismatch."
            )

        if signature.content_digest != expected_content_digest:
            raise SignatureVerificationError(
                "Signature contains a content digest mismatch."
            )

    @staticmethod
    def _validate_verification_time(
        verified_at: datetime,
        *,
        signature: DetachedSignature,
    ) -> None:
        if not isinstance(verified_at, datetime):
            raise TypeError(
                "verified_at must be a datetime."
            )

        if (
            verified_at.tzinfo is None
            or verified_at.utcoffset() is None
        ):
            raise SignatureVerificationError(
                "verified_at must be timezone-aware."
            )

        if verified_at < signature.signed_at:
            raise SignatureVerificationError(
                "Verification cannot occur before signature creation."
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
            raise SignatureVerificationError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise SignatureVerificationError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise SignatureVerificationError(
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
            raise SignatureVerificationError(
                f"{field_name} must not be empty."
            )