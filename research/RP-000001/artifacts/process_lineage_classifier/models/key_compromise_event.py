from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class KeyCompromiseEvent:
    """Immutable observer-only record of a confirmed key compromise."""

    event_id: str
    key_id: str
    material_id: str
    public_key_fingerprint: str

    owner_id: str
    issuer_id: str

    compromise_type: str
    evidence_digest: str

    detected_at: datetime
    effective_at: datetime
    recorded_at: datetime

    reported_by: str
    description: str

    confirmed: bool
    historical_signatures_invalidated: bool

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("event_id", self.event_id),
            ("key_id", self.key_id),
            ("material_id", self.material_id),
            ("owner_id", self.owner_id),
            ("issuer_id", self.issuer_id),
            ("compromise_type", self.compromise_type),
            ("reported_by", self.reported_by),
            ("description", self.description),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            self.public_key_fingerprint,
            "public_key_fingerprint",
        )
        self._validate_digest(
            self.evidence_digest,
            "evidence_digest",
        )

        if self.compromise_type not in {
            "PRIVATE_KEY_EXPOSURE",
            "UNAUTHORIZED_KEY_USE",
            "KEY_MATERIAL_LOSS",
            "UNKNOWN_COMPROMISE",
        }:
            raise ValueError(
                "compromise_type must be "
                "PRIVATE_KEY_EXPOSURE, "
                "UNAUTHORIZED_KEY_USE, "
                "KEY_MATERIAL_LOSS, or "
                "UNKNOWN_COMPROMISE."
            )

        self._validate_datetime(
            self.detected_at,
            "detected_at",
        )
        self._validate_datetime(
            self.effective_at,
            "effective_at",
        )
        self._validate_datetime(
            self.recorded_at,
            "recorded_at",
        )

        if self.detected_at < self.effective_at:
            raise ValueError(
                "detected_at cannot be before effective_at."
            )

        if self.recorded_at < self.detected_at:
            raise ValueError(
                "recorded_at cannot be before detected_at."
            )

        if not isinstance(self.confirmed, bool):
            raise TypeError(
                "confirmed must be a boolean."
            )

        if not isinstance(
            self.historical_signatures_invalidated,
            bool,
        ):
            raise TypeError(
                "historical_signatures_invalidated "
                "must be a boolean."
            )

        if self.historical_signatures_invalidated is not False:
            raise ValueError(
                "KeyCompromiseEvent must not automatically "
                "invalidate historical signatures."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "KeyCompromiseEvent must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "KeyCompromiseEvent must not permit side effects."
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