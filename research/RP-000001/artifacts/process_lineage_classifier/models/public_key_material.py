from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PublicKeyMaterial:
    """Immutable observer-only representation of public-key material."""

    material_id: str
    key_id: str
    owner_id: str

    algorithm: str
    encoding: str
    public_key_value: str
    public_key_fingerprint: str

    created_at: datetime
    valid_from: datetime
    valid_until: datetime

    issuer_id: str
    revoked: bool

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("material_id", self.material_id),
            ("key_id", self.key_id),
            ("owner_id", self.owner_id),
            ("algorithm", self.algorithm),
            ("encoding", self.encoding),
            ("public_key_value", self.public_key_value),
            ("issuer_id", self.issuer_id),
        ):
            self._require_non_empty(value, field_name)

        if self.algorithm != "ED25519":
            raise ValueError(
                "algorithm must be ED25519."
            )

        if self.encoding != "HEX":
            raise ValueError(
                "encoding must be HEX."
            )

        self._validate_public_key_value(
            self.public_key_value,
        )
        self._validate_fingerprint(
            self.public_key_fingerprint,
            "public_key_fingerprint",
        )

        self._validate_datetime(
            self.created_at,
            "created_at",
        )
        self._validate_datetime(
            self.valid_from,
            "valid_from",
        )
        self._validate_datetime(
            self.valid_until,
            "valid_until",
        )

        if self.valid_from < self.created_at:
            raise ValueError(
                "valid_from cannot be before created_at."
            )

        if self.valid_until <= self.valid_from:
            raise ValueError(
                "valid_until must be after valid_from."
            )

        if not isinstance(self.revoked, bool):
            raise TypeError(
                "revoked must be a boolean."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "PublicKeyMaterial must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "PublicKeyMaterial must not permit side effects."
            )

    @staticmethod
    def _validate_public_key_value(
        public_key_value: str,
    ) -> None:
        prefix = "ed25519:"

        if not public_key_value.startswith(prefix):
            raise ValueError(
                "public_key_value must use the ed25519 prefix."
            )

        encoded_key = public_key_value.removeprefix(prefix)

        if len(encoded_key) != 64:
            raise ValueError(
                "public_key_value must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in encoded_key
        ):
            raise ValueError(
                "public_key_value must contain only lowercase "
                "hexadecimal characters."
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
    def _validate_datetime(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(
                f"{field_name} must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must be timezone-aware."
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