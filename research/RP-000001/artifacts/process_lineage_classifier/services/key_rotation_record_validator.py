from models import KeyRotationRecord


class KeyRotationRecordError(ValueError):
    """Raised when a key-rotation record fails validation."""


class KeyRotationRecordValidator:
    """Validates key-rotation identities, fingerprints, and algorithm."""

    def validate(
        self,
        record: KeyRotationRecord,
        *,
        expected_owner_id: str | None = None,
        expected_previous_key_id: str | None = None,
        expected_previous_fingerprint: str | None = None,
        expected_new_key_id: str | None = None,
        expected_new_fingerprint: str | None = None,
        expected_algorithm: str | None = None,
    ) -> bool:
        if not isinstance(record, KeyRotationRecord):
            raise TypeError(
                "record must be a KeyRotationRecord."
            )

        expected_values = (
            expected_owner_id,
            expected_previous_key_id,
            expected_previous_fingerprint,
            expected_new_key_id,
            expected_new_fingerprint,
            expected_algorithm,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise KeyRotationRecordError(
                "Key-rotation validation requires a complete expected "
                "reference set."
            )

        self._require_non_empty(
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_non_empty(
            expected_previous_key_id,
            "expected_previous_key_id",
        )
        self._require_fingerprint(
            expected_previous_fingerprint,
            "expected_previous_fingerprint",
        )
        self._require_non_empty(
            expected_new_key_id,
            "expected_new_key_id",
        )
        self._require_fingerprint(
            expected_new_fingerprint,
            "expected_new_fingerprint",
        )
        self._require_non_empty(
            expected_algorithm,
            "expected_algorithm",
        )

        comparisons = (
            (
                record.owner_id,
                expected_owner_id,
                "owner identity",
            ),
            (
                record.previous_key_id,
                expected_previous_key_id,
                "previous key identity",
            ),
            (
                record.previous_key_fingerprint,
                expected_previous_fingerprint,
                "previous key fingerprint",
            ),
            (
                record.new_key_id,
                expected_new_key_id,
                "new key identity",
            ),
            (
                record.new_key_fingerprint,
                expected_new_fingerprint,
                "new key fingerprint",
            ),
            (
                record.algorithm,
                expected_algorithm,
                "algorithm",
            ),
        )

        for actual, expected, label in comparisons:
            if actual != expected:
                raise KeyRotationRecordError(
                    f"Key-rotation record contains a {label} mismatch."
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