from models import KeyRevocationRecord


class KeyRevocationRecordError(ValueError):
    """Raised when a key-revocation record fails validation."""


class KeyRevocationRecordValidator:
    """Validates key-revocation identity and permanent revocation state."""

    def validate(
        self,
        record: KeyRevocationRecord,
        *,
        expected_key_id: str | None = None,
        expected_owner_id: str | None = None,
        expected_fingerprint: str | None = None,
        expected_algorithm: str | None = None,
    ) -> bool:
        if not isinstance(record, KeyRevocationRecord):
            raise TypeError(
                "record must be a KeyRevocationRecord."
            )

        if record.permanent is not True:
            raise KeyRevocationRecordError(
                "Key revocation must be permanent."
            )

        expected_values = (
            expected_key_id,
            expected_owner_id,
            expected_fingerprint,
            expected_algorithm,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise KeyRevocationRecordError(
                "Key-revocation validation requires a complete "
                "expected reference set."
            )

        self._require_non_empty(
            expected_key_id,
            "expected_key_id",
        )
        self._require_non_empty(
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_fingerprint(
            expected_fingerprint,
            "expected_fingerprint",
        )
        self._require_non_empty(
            expected_algorithm,
            "expected_algorithm",
        )

        comparisons = (
            (
                record.key_id,
                expected_key_id,
                "key identity",
            ),
            (
                record.owner_id,
                expected_owner_id,
                "owner identity",
            ),
            (
                record.key_fingerprint,
                expected_fingerprint,
                "key fingerprint",
            ),
            (
                record.algorithm,
                expected_algorithm,
                "algorithm",
            ),
        )

        for actual, expected, label in comparisons:
            if actual != expected:
                raise KeyRevocationRecordError(
                    f"Key-revocation record contains a {label} mismatch."
                )

        return True

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

    @staticmethod
    def _require_fingerprint(
        value: str | None,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not value.startswith(prefix):
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        fingerprint_value = value.removeprefix(prefix)

        if len(fingerprint_value) != 64:
            raise ValueError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in fingerprint_value
        ):
            raise ValueError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )