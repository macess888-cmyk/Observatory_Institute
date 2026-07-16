from models import RegistryVersionRecord


class RegistryVersionRecordError(ValueError):
    """Raised when registry version record validation fails."""


class RegistryVersionRecordValidator:
    """Validates registry-version transition references."""

    def validate(
        self,
        record: RegistryVersionRecord,
        *,
        expected_registry_id: str | None = None,
        expected_registry_version: str | None = None,
        expected_previous_registry_version: str | None = None,
        expected_snapshot_id: str | None = None,
        expected_previous_snapshot_id: str | None = None,
        expected_transition_type: str | None = None,
        expected_transition_receipt_id: str | None = None,
    ) -> bool:
        if not isinstance(record, RegistryVersionRecord):
            raise TypeError(
                "record must be a RegistryVersionRecord."
            )

        expected_values = (
            expected_registry_id,
            expected_registry_version,
            expected_previous_registry_version,
            expected_snapshot_id,
            expected_previous_snapshot_id,
            expected_transition_type,
            expected_transition_receipt_id,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise RegistryVersionRecordError(
                "Registry version validation requires a complete "
                "expected reference set."
            )

        self._require_non_empty(
            expected_registry_id,
            "expected_registry_id",
        )
        self._require_non_empty(
            expected_registry_version,
            "expected_registry_version",
        )
        self._require_non_empty(
            expected_previous_registry_version,
            "expected_previous_registry_version",
        )
        self._require_non_empty(
            expected_snapshot_id,
            "expected_snapshot_id",
        )
        self._require_non_empty(
            expected_previous_snapshot_id,
            "expected_previous_snapshot_id",
        )
        self._require_non_empty(
            expected_transition_type,
            "expected_transition_type",
        )
        self._require_non_empty(
            expected_transition_receipt_id,
            "expected_transition_receipt_id",
        )

        if record.registry_id != expected_registry_id:
            raise RegistryVersionRecordError(
                "Registry version record contains a registry "
                "identity mismatch."
            )

        if (
            record.registry_version
            != expected_registry_version
        ):
            raise RegistryVersionRecordError(
                "Registry version record contains a registry "
                "version mismatch."
            )

        if (
            record.previous_registry_version
            != expected_previous_registry_version
        ):
            raise RegistryVersionRecordError(
                "Registry version record contains a previous "
                "registry version mismatch."
            )

        if record.snapshot_id != expected_snapshot_id:
            raise RegistryVersionRecordError(
                "Registry version record contains a snapshot "
                "identity mismatch."
            )

        if (
            record.previous_snapshot_id
            != expected_previous_snapshot_id
        ):
            raise RegistryVersionRecordError(
                "Registry version record contains a previous "
                "snapshot identity mismatch."
            )

        if (
            record.transition_type
            != expected_transition_type
        ):
            raise RegistryVersionRecordError(
                "Registry version record contains a transition "
                "type mismatch."
            )

        if (
            record.transition_receipt_id
            != expected_transition_receipt_id
        ):
            raise RegistryVersionRecordError(
                "Registry version record contains a transition "
                "receipt identity mismatch."
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
            raise RegistryVersionRecordError(
                f"{field_name} must not be empty."
            )