from datetime import datetime

from models import SigningKeyIdentity


class SigningKeyIdentityError(ValueError):
    """Raised when a signing-key identity fails validation."""


class SigningKeyIdentityValidator:
    """Validates signing-key identity, ownership, and validity state."""

    def validate(
        self,
        key: SigningKeyIdentity,
        *,
        now: datetime,
        expected_owner_id: str | None = None,
        expected_issuer_id: str | None = None,
    ) -> bool:
        if not isinstance(key, SigningKeyIdentity):
            raise TypeError(
                "key must be a SigningKeyIdentity."
            )

        self._validate_reference_time(now)

        if key.revoked:
            raise SigningKeyIdentityError(
                "Signing key has been revoked."
            )

        if now < key.valid_from:
            raise SigningKeyIdentityError(
                "Signing key is not yet valid."
            )

        if now > key.valid_until:
            raise SigningKeyIdentityError(
                "Signing key has expired."
            )

        expected_values = (
            expected_owner_id,
            expected_issuer_id,
        )

        if all(value is None for value in expected_values):
            return True

        self._require_non_empty(
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_non_empty(
            expected_issuer_id,
            "expected_issuer_id",
        )

        if key.owner_id != expected_owner_id:
            raise SigningKeyIdentityError(
                "Signing key contains an owner identity mismatch."
            )

        if key.issuer_id != expected_issuer_id:
            raise SigningKeyIdentityError(
                "Signing key contains an issuer identity mismatch."
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
            raise SigningKeyIdentityError(
                "now must be timezone-aware."
            )

    @staticmethod
    def _require_non_empty(
        value: str | None,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be empty."
            )