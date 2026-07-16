from models import TrustedKeyRegistrySnapshot


class TrustedKeyRegistrySnapshotError(ValueError):
    """Raised when trusted-key registry snapshot validation fails."""


class TrustedKeyRegistrySnapshotValidator:
    """Validates trusted-key registry snapshot references and integrity."""

    def validate(
        self,
        snapshot: TrustedKeyRegistrySnapshot,
        *,
        expected_registry_id: str | None = None,
        expected_registry_version: str | None = None,
        expected_owner_id: str | None = None,
        expected_issuer_id: str | None = None,
        expected_material_count: int | None = None,
    ) -> bool:
        if not isinstance(
            snapshot,
            TrustedKeyRegistrySnapshot,
        ):
            raise TypeError(
                "snapshot must be a TrustedKeyRegistrySnapshot."
            )

        expected_values = (
            expected_registry_id,
            expected_registry_version,
            expected_owner_id,
            expected_issuer_id,
            expected_material_count,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise TrustedKeyRegistrySnapshotError(
                "Snapshot validation requires a complete expected "
                "reference set."
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
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_non_empty(
            expected_issuer_id,
            "expected_issuer_id",
        )

        if not isinstance(expected_material_count, int):
            raise TypeError(
                "expected_material_count must be an integer."
            )

        if expected_material_count < 1:
            raise TrustedKeyRegistrySnapshotError(
                "expected_material_count must be at least 1."
            )

        if snapshot.registry_id != expected_registry_id:
            raise TrustedKeyRegistrySnapshotError(
                "Snapshot contains a registry identity mismatch."
            )

        if (
            snapshot.registry_version
            != expected_registry_version
        ):
            raise TrustedKeyRegistrySnapshotError(
                "Snapshot contains a registry version mismatch."
            )

        if snapshot.owner_id != expected_owner_id:
            raise TrustedKeyRegistrySnapshotError(
                "Snapshot contains an owner identity mismatch."
            )

        if snapshot.issuer_id != expected_issuer_id:
            raise TrustedKeyRegistrySnapshotError(
                "Snapshot contains an issuer identity mismatch."
            )

        if (
            len(snapshot.materials)
            != expected_material_count
        ):
            raise TrustedKeyRegistrySnapshotError(
                "Snapshot contains a material count mismatch."
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
            raise TrustedKeyRegistrySnapshotError(
                f"{field_name} must not be empty."
            )