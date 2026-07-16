from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TrustedKeyAdmissionReceipt:
    """Immutable observer-only receipt for trusted-key admission."""

    receipt_id: str
    registry_id: str
    registry_version: str
    previous_registry_version: str

    snapshot_id: str
    snapshot_digest: str

    material_id: str
    key_id: str
    public_key_fingerprint: str

    owner_id: str
    issuer_id: str

    admitted_by: str
    admission_reason: str
    admitted_at: datetime

    admitted: bool

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
            ("snapshot_id", self.snapshot_id),
            ("material_id", self.material_id),
            ("key_id", self.key_id),
            ("owner_id", self.owner_id),
            ("issuer_id", self.issuer_id),
            ("admitted_by", self.admitted_by),
            ("admission_reason", self.admission_reason),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            self.snapshot_digest,
            "snapshot_digest",
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

        self._validate_datetime(
            self.admitted_at,
            "admitted_at",
        )

        if not isinstance(self.admitted, bool):
            raise TypeError(
                "admitted must be a boolean."
            )

        if self.admitted is not True:
            raise ValueError(
                "TrustedKeyAdmissionReceipt must record admission."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "TrustedKeyAdmissionReceipt must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "TrustedKeyAdmissionReceipt must not permit side effects."
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