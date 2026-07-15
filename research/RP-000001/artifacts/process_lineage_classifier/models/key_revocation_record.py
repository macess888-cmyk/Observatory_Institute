from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class KeyRevocationRecord:
    """Immutable observer-only record of signing-key revocation."""

    revocation_id: str
    key_id: str
    owner_id: str
    key_fingerprint: str
    algorithm: str

    revoked_at: datetime
    revoked_by: str
    reason: str
    permanent: bool

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("revocation_id", self.revocation_id),
            ("key_id", self.key_id),
            ("owner_id", self.owner_id),
            ("algorithm", self.algorithm),
            ("revoked_by", self.revoked_by),
            ("reason", self.reason),
        ):
            self._require_non_empty(value, field_name)

        if self.algorithm != "ED25519":
            raise ValueError(
                "algorithm must be ED25519."
            )

        self._validate_fingerprint(
            self.key_fingerprint,
            "key_fingerprint",
        )

        if not isinstance(self.revoked_at, datetime):
            raise TypeError(
                "revoked_at must be a datetime."
            )

        if (
            self.revoked_at.tzinfo is None
            or self.revoked_at.utcoffset() is None
        ):
            raise ValueError(
                "revoked_at must be timezone-aware."
            )

        if not isinstance(self.permanent, bool):
            raise TypeError(
                "permanent must be a boolean."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "KeyRevocationRecord must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "KeyRevocationRecord must not permit side effects."
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