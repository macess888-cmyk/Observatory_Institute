from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RegistryVersionRecord:
    """Immutable observer-only record of a registry version transition."""

    record_id: str
    registry_id: str
    registry_version: str
    previous_registry_version: str

    snapshot_id: str
    snapshot_digest: str
    previous_snapshot_id: str
    previous_snapshot_digest: str

    transition_type: str
    transition_receipt_id: str
    transition_receipt_digest: str

    recorded_at: datetime

    owner_id: str
    issuer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("record_id", self.record_id),
            ("registry_id", self.registry_id),
            ("registry_version", self.registry_version),
            (
                "previous_registry_version",
                self.previous_registry_version,
            ),
            ("snapshot_id", self.snapshot_id),
            (
                "previous_snapshot_id",
                self.previous_snapshot_id,
            ),
            ("transition_type", self.transition_type),
            (
                "transition_receipt_id",
                self.transition_receipt_id,
            ),
            ("owner_id", self.owner_id),
            ("issuer_id", self.issuer_id),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            self.snapshot_digest,
            "snapshot_digest",
        )
        self._validate_digest(
            self.previous_snapshot_digest,
            "previous_snapshot_digest",
        )
        self._validate_digest(
            self.transition_receipt_digest,
            "transition_receipt_digest",
        )

        if (
            self.registry_version
            == self.previous_registry_version
        ):
            raise ValueError(
                "registry version transition must change version."
            )

        if self.snapshot_id == self.previous_snapshot_id:
            raise ValueError(
                "snapshot transition must change snapshot identity."
            )

        if (
            self.snapshot_digest
            == self.previous_snapshot_digest
        ):
            raise ValueError(
                "snapshot digest transition must change digest."
            )

        if self.transition_type not in {
            "ADMISSION",
            "REMOVAL",
        }:
            raise ValueError(
                "transition_type must be ADMISSION or REMOVAL."
            )

        self._validate_datetime(
            self.recorded_at,
            "recorded_at",
        )

        if self.execution_requested is not False:
            raise ValueError(
                "RegistryVersionRecord must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RegistryVersionRecord must not permit side effects."
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

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
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
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise ValueError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise ValueError(
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
            raise ValueError(
                f"{field_name} must not be empty."
            )