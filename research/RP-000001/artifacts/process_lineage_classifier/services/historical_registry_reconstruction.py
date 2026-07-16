from models import (
    RegistryVersionRecord,
    TrustedKeyRegistrySnapshot,
)
from services.trusted_key_registry_snapshot_hasher import (
    TrustedKeyRegistrySnapshotHasher,
)


class HistoricalRegistryReconstructionError(ValueError):
    """Raised when historical registry reconstruction fails."""


class HistoricalRegistryReconstructionService:
    """Reconstructs a trusted-key registry snapshot at a requested version."""

    def reconstruct(
        self,
        *,
        registry_id: str,
        target_registry_version: str,
        snapshots: tuple[
            TrustedKeyRegistrySnapshot,
            ...,
        ],
        version_records: tuple[
            RegistryVersionRecord,
            ...,
        ],
    ) -> TrustedKeyRegistrySnapshot:
        self._require_non_empty(
            registry_id,
            "registry_id",
        )
        self._require_non_empty(
            target_registry_version,
            "target_registry_version",
        )

        if not isinstance(snapshots, tuple):
            raise TypeError(
                "snapshots must be a tuple."
            )

        if not isinstance(version_records, tuple):
            raise TypeError(
                "version_records must be a tuple."
            )

        if not snapshots:
            raise HistoricalRegistryReconstructionError(
                "snapshots must not be empty."
            )

        for snapshot in snapshots:
            if not isinstance(
                snapshot,
                TrustedKeyRegistrySnapshot,
            ):
                raise TypeError(
                    "snapshots must contain only "
                    "TrustedKeyRegistrySnapshot."
                )

        for record in version_records:
            if not isinstance(
                record,
                RegistryVersionRecord,
            ):
                raise TypeError(
                    "version_records must contain only "
                    "RegistryVersionRecord."
                )

        snapshots_by_version = self._index_snapshots(
            snapshots,
            registry_id=registry_id,
        )
        records_by_version = self._index_records(
            version_records,
            registry_id=registry_id,
        )

        if (
            target_registry_version
            not in snapshots_by_version
        ):
            raise HistoricalRegistryReconstructionError(
                "Unknown target registry version."
            )

        self._validate_version_records(
            snapshots_by_version=snapshots_by_version,
            records_by_version=records_by_version,
        )

        target_snapshot = snapshots_by_version[
            target_registry_version
        ]

        if target_registry_version in records_by_version:
            self._validate_record_binding(
                record=records_by_version[
                    target_registry_version
                ],
                current_snapshot=target_snapshot,
                previous_snapshot=snapshots_by_version[
                    records_by_version[
                        target_registry_version
                    ].previous_registry_version
                ],
            )

        return target_snapshot

    @staticmethod
    def _index_snapshots(
        snapshots: tuple[
            TrustedKeyRegistrySnapshot,
            ...,
        ],
        *,
        registry_id: str,
    ) -> dict[str, TrustedKeyRegistrySnapshot]:
        indexed: dict[
            str,
            TrustedKeyRegistrySnapshot,
        ] = {}

        for snapshot in snapshots:
            if snapshot.registry_id != registry_id:
                raise HistoricalRegistryReconstructionError(
                    "Snapshot contains a registry identity mismatch."
                )

            if snapshot.registry_version in indexed:
                raise HistoricalRegistryReconstructionError(
                    "Snapshot set contains a duplicate snapshot version."
                )

            indexed[
                snapshot.registry_version
            ] = snapshot

        return indexed

    @staticmethod
    def _index_records(
        records: tuple[
            RegistryVersionRecord,
            ...,
        ],
        *,
        registry_id: str,
    ) -> dict[str, RegistryVersionRecord]:
        indexed: dict[
            str,
            RegistryVersionRecord,
        ] = {}

        for record in records:
            if record.registry_id != registry_id:
                raise HistoricalRegistryReconstructionError(
                    "Version record contains a registry "
                    "identity mismatch."
                )

            if record.registry_version in indexed:
                raise HistoricalRegistryReconstructionError(
                    "Version record set contains a duplicate "
                    "version record."
                )

            indexed[
                record.registry_version
            ] = record

        return indexed

    def _validate_version_records(
        self,
        *,
        snapshots_by_version: dict[
            str,
            TrustedKeyRegistrySnapshot,
        ],
        records_by_version: dict[
            str,
            RegistryVersionRecord,
        ],
    ) -> None:
        ordered_records = sorted(
            records_by_version.values(),
            key=lambda record: record.recorded_at,
        )

        previous_record: (
            RegistryVersionRecord | None
        ) = None

        for record in ordered_records:
            if (
                record.registry_version
                not in snapshots_by_version
            ):
                raise HistoricalRegistryReconstructionError(
                    "Version record references an unknown "
                    "snapshot version."
                )

            if (
                record.previous_registry_version
                not in snapshots_by_version
            ):
                raise HistoricalRegistryReconstructionError(
                    "Version record references an unknown "
                    "previous registry version."
                )

            if (
                previous_record is not None
                and record.previous_registry_version
                != previous_record.registry_version
            ):
                raise HistoricalRegistryReconstructionError(
                    "Registry version chain is broken."
                )

            current_snapshot = snapshots_by_version[
                record.registry_version
            ]
            previous_snapshot = snapshots_by_version[
                record.previous_registry_version
            ]

            self._validate_record_binding(
                record=record,
                current_snapshot=current_snapshot,
                previous_snapshot=previous_snapshot,
            )

            previous_record = record

    @staticmethod
    def _validate_record_binding(
        *,
        record: RegistryVersionRecord,
        current_snapshot: TrustedKeyRegistrySnapshot,
        previous_snapshot: TrustedKeyRegistrySnapshot,
    ) -> None:
        if record.snapshot_id != current_snapshot.snapshot_id:
            raise HistoricalRegistryReconstructionError(
                "Version record contains a snapshot identity mismatch."
            )

        if (
            record.previous_snapshot_id
            != previous_snapshot.snapshot_id
        ):
            raise HistoricalRegistryReconstructionError(
                "Version record contains a previous "
                "snapshot identity mismatch."
            )

        hasher = TrustedKeyRegistrySnapshotHasher()

        current_digest = hasher.hash(
            current_snapshot
        )
        previous_digest = hasher.hash(
            previous_snapshot
        )

        if record.snapshot_digest != current_digest:
            raise HistoricalRegistryReconstructionError(
                "Version record contains a snapshot digest mismatch."
            )

        if (
            record.previous_snapshot_digest
            != previous_digest
        ):
            raise HistoricalRegistryReconstructionError(
                "Version record contains a previous "
                "snapshot digest mismatch."
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
            raise HistoricalRegistryReconstructionError(
                f"{field_name} must not be empty."
            )