from models import KeyCompromiseEvent


class KeyCompromiseEventError(ValueError):
    """Raised when key-compromise event validation fails."""


class KeyCompromiseEventValidator:
    """Validates confirmed key-compromise evidence and references."""

    def validate(
        self,
        event: KeyCompromiseEvent,
        *,
        expected_key_id: str | None = None,
        expected_material_id: str | None = None,
        expected_owner_id: str | None = None,
        expected_issuer_id: str | None = None,
        expected_fingerprint: str | None = None,
    ) -> bool:
        if not isinstance(event, KeyCompromiseEvent):
            raise TypeError(
                "event must be a KeyCompromiseEvent."
            )

        if not isinstance(event.confirmed, bool):
            raise TypeError(
                "confirmed must be a boolean."
            )

        if event.confirmed is not True:
            raise KeyCompromiseEventError(
                "Key-compromise event must be confirmed."
            )

        expected_values = (
            expected_key_id,
            expected_material_id,
            expected_owner_id,
            expected_issuer_id,
            expected_fingerprint,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise KeyCompromiseEventError(
                "Key-compromise validation requires a complete "
                "expected reference set."
            )

        self._require_non_empty(
            expected_key_id,
            "expected_key_id",
        )
        self._require_non_empty(
            expected_material_id,
            "expected_material_id",
        )
        self._require_non_empty(
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_non_empty(
            expected_issuer_id,
            "expected_issuer_id",
        )
        self._validate_digest(
            expected_fingerprint,
            "expected_fingerprint",
        )

        if event.key_id != expected_key_id:
            raise KeyCompromiseEventError(
                "Key-compromise event contains a key identity mismatch."
            )

        if event.material_id != expected_material_id:
            raise KeyCompromiseEventError(
                "Key-compromise event contains a material "
                "identity mismatch."
            )

        if event.owner_id != expected_owner_id:
            raise KeyCompromiseEventError(
                "Key-compromise event contains an owner "
                "identity mismatch."
            )

        if event.issuer_id != expected_issuer_id:
            raise KeyCompromiseEventError(
                "Key-compromise event contains an issuer "
                "identity mismatch."
            )

        if event.public_key_fingerprint != expected_fingerprint:
            raise KeyCompromiseEventError(
                "Key-compromise event contains a fingerprint mismatch."
            )

        return True

    @staticmethod
    def _validate_digest(
        digest: str | None,
        field_name: str,
    ) -> None:
        if not isinstance(digest, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not digest.startswith(prefix):
            raise KeyCompromiseEventError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise KeyCompromiseEventError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise KeyCompromiseEventError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
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
            raise KeyCompromiseEventError(
                f"{field_name} must not be empty."
            )