from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class KeyRotationRecord:
    """Immutable observer-only record of signing-key rotation."""

    rotation_id: str
    owner_id: str

    previous_key_id: str
    previous_key_fingerprint: str

    new_key_id: str
    new_key_fingerprint: str

    algorithm: str
    rotated_at: datetime
    rotated_by: str
    reason: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("rotation_id", self.rotation_id),
            ("owner_id", self.owner_id),
            ("previous_key_id", self.previous_key_id),
            ("new_key_id", self.new_key_id),
            ("algorithm", self.algorithm),
            ("rotated_by", self.rotated_by),
            ("reason", self.reason),
        ):
            self._require_non_empty(value, field_name)

        if self.previous_key_id == self.new_key_id:
            raise ValueError(
                "previous_key_id and new_key_id must be different."
            )

        if self.algorithm != "ED25519":
            raise ValueError(
                "algorithm must be ED25519."
            )

        self._validate_fingerprint(
            self.previous_key_fingerprint,
            "previous_key_fingerprint",
        )
        self._validate_fingerprint(
            self.new_key_fingerprint,
            "new_key_fingerprint",
        )

        if (
            self.previous_key_fingerprint
            == self.new_key_fingerprint
        ):
            raise ValueError(
                "Previous and new key fingerprints must be different."
            )

        if not isinstance(self.rotated_at, datetime):
            raise TypeError(
                "rotated_at must be a datetime."
            )

        if (
            self.rotated_at.tzinfo is None
            or self.rotated_at.utcoffset() is None
        ):
            raise ValueError(
                "rotated_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "KeyRotationRecord must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "KeyRotationRecord must not permit side effects."
            )

    @staticmethod
    def _validate_fingerprint(
        fingerprint: str,
        field_name: str,
    ) -> None:
        if not isinstance(fingerprint, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not fingerprint.startswith(prefix):
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        fingerprint_value = fingerprint.removeprefix(prefix)

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