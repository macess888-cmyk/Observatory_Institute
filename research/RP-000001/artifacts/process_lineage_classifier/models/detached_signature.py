from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DetachedSignature:
    """Immutable observer-only detached signature record."""

    signature_id: str
    key_id: str

    subject_id: str
    subject_type: str
    content_digest: str

    algorithm: str
    signature_value: str

    signed_at: datetime
    signer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("signature_id", self.signature_id),
            ("key_id", self.key_id),
            ("subject_id", self.subject_id),
            ("subject_type", self.subject_type),
            ("algorithm", self.algorithm),
            ("signature_value", self.signature_value),
            ("signer_id", self.signer_id),
        ):
            self._require_non_empty(value, field_name)

        if self.algorithm != "ED25519":
            raise ValueError(
                "algorithm must be ED25519."
            )

        self._validate_digest(
            self.content_digest,
            "content_digest",
        )
        self._validate_signature_value(
            self.signature_value,
        )
        self._validate_datetime(
            self.signed_at,
            "signed_at",
        )

        if self.execution_requested is not False:
            raise ValueError(
                "DetachedSignature must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "DetachedSignature must not permit side effects."
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
                f"{field_name} must contain 64 hexadecimal characters."
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
    def _validate_signature_value(
        signature_value: str,
    ) -> None:
        prefix = "ed25519:"

        if not signature_value.startswith(prefix):
            raise ValueError(
                "signature_value must use the ed25519 prefix."
            )

        encoded_signature = signature_value.removeprefix(prefix)

        if len(encoded_signature) != 128:
            raise ValueError(
                "signature_value must contain 128 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in encoded_signature
        ):
            raise ValueError(
                "signature_value must contain only lowercase "
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