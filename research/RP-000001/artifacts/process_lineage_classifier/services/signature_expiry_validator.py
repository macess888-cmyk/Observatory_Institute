from datetime import datetime

from models import (
    DetachedSignature,
    SigningKeyIdentity,
)


class SignatureExpiryError(ValueError):
    """Raised when signature or key temporal validity fails."""


class SignatureExpiryValidator:
    """Validates signature timing against signing-key validity."""

    def validate(
        self,
        signature: DetachedSignature,
        key: SigningKeyIdentity,
        *,
        now: datetime,
    ) -> bool:
        if not isinstance(signature, DetachedSignature):
            raise TypeError(
                "signature must be a DetachedSignature."
            )

        if not isinstance(key, SigningKeyIdentity):
            raise TypeError(
                "key must be a SigningKeyIdentity."
            )

        self._validate_reference_time(now)

        if signature.key_id != key.key_id:
            raise SignatureExpiryError(
                "Signature contains a key identity mismatch."
            )

        if signature.signer_id != key.owner_id:
            raise SignatureExpiryError(
                "Signature contains a signer identity mismatch."
            )

        if signature.algorithm != key.algorithm:
            raise SignatureExpiryError(
                "Signature and signing key contain an algorithm mismatch."
            )

        if key.revoked:
            raise SignatureExpiryError(
                "Signing key has been revoked."
            )

        if signature.signed_at < key.valid_from:
            raise SignatureExpiryError(
                "Signature was created before key validity began."
            )

        if signature.signed_at > key.valid_until:
            raise SignatureExpiryError(
                "Signature was created after key validity ended."
            )

        if now < signature.signed_at:
            raise SignatureExpiryError(
                "Reference time cannot occur before signature creation."
            )

        if now > key.valid_until:
            raise SignatureExpiryError(
                "Signing key has expired."
            )

        return True

    @staticmethod
    def _validate_reference_time(
        now: datetime,
    ) -> None:
        if not isinstance(now, datetime):
            raise TypeError(
                "now must be a datetime."
            )

        if now.tzinfo is None or now.utcoffset() is None:
            raise SignatureExpiryError(
                "now must be timezone-aware."
            )