from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TrustedKeyRemovalReceipt:
    """Immutable observer-only receipt for trusted-key removal."""

    receipt_id: str
    registry_id: str
    registry_version: str
    previous_registry_version: str

    previous_snapshot_id: str
    previous_snapshot_digest: str
    current_snapshot_id: str
    current_snapshot_digest: str

    material_id: str
    key_id: str
    public_key_fingerprint: str

    owner_id: str
    issuer_id: str

    removed_by: str
    removal_reason: str
    removed_at: datetime

    removed: bool
    retroactive_invalidation: bool

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("receipt_id", self.receipt_id),
            ("registry_id", self.registry_id),
            ("registry_version", self.registry_version),
            (
                "previous_registry_version",
                self.previous_registry_version,
            ),
            (
                "previous_snapshot_id",
                self.previous_snapshot_id,
            ),
            (
                "current_snapshot_id",
                self.current_snapshot_id,
            ),
            ("material_id", self.material_id),
            ("key_id", self.key_id),
            ("owner_id", self.owner_id),
            ("issuer_id", self.issuer_id),
            ("removed_by", self.removed_by),
            ("removal_reason", self.removal_reason),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            self.previous_snapshot_digest,
            "previous_snapshot_digest",
        )
        self._validate_digest(
            self.current_snapshot_digest,
            "current_snapshot_digest",
        )
        self._validate_digest(
            self.public_key_fingerprint,
            "public_key_fingerprint",
        )

        if (
            self.registry_version
            == self.previous_registry_version
        ):
            raise ValueError(
                "registry version transition must change version."
            )

        if (
            self.previous_snapshot_id
            == self.current_snapshot_id
        ):
            raise ValueError(
                "snapshot transition must change snapshot identity."
            )

        if (
            self.previous_snapshot_digest
            == self.current_snapshot_digest
        ):
            raise ValueError(
                "snapshot digest transition must change digest."
            )

        self._validate_datetime(
            self.removed_at,
            "removed_at",
        )

        if not isinstance(self.removed, bool):
            raise TypeError(
                "removed must be a boolean."
            )

        if self.removed is not True:
            raise ValueError(
                "TrustedKeyRemovalReceipt must record removal."
            )

        if not isinstance(
            self.retroactive_invalidation,
            bool,
        ):
            raise TypeError(
                "retroactive_invalidation must be a boolean."
            )

        if self.retroactive_invalidation is not False:
            raise ValueError(
                "TrustedKeyRemovalReceipt must not claim "
                "retroactive invalidation."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "TrustedKeyRemovalReceipt must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "TrustedKeyRemovalReceipt must not permit side effects."
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