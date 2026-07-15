from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SignatureVerification:
    """Immutable observer-only result of detached-signature verification."""

    verification_id: str
    signature_id: str
    key_id: str
    subject_id: str
    subject_type: str
    content_digest: str
    signer_id: str
    key_owner_id: str
    algorithm: str
    signature_verified: bool
    key_valid: bool
    identity_match: bool
    content_match: bool
    verified: bool
    verified_at: datetime
    verifier_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("verification_id", self.verification_id),
            ("signature_id", self.signature_id),
            ("key_id", self.key_id),
            ("subject_id", self.subject_id),
            ("subject_type", self.subject_type),
            ("content_digest", self.content_digest),
            ("signer_id", self.signer_id),
            ("key_owner_id", self.key_owner_id),
            ("algorithm", self.algorithm),
            ("verifier_id", self.verifier_id),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(self.content_digest, "content_digest")

        if self.algorithm != "ED25519":
            raise ValueError("algorithm must be ED25519.")

        for field_name, value in (
            ("signature_verified", self.signature_verified),
            ("key_valid", self.key_valid),
            ("identity_match", self.identity_match),
            ("content_match", self.content_match),
            ("verified", self.verified),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a boolean.")

        expected_verified = all((
            self.signature_verified,
            self.key_valid,
            self.identity_match,
            self.content_match,
        ))

        if self.verified is not expected_verified:
            raise ValueError(
                "verified must match the signature-verification results."
            )

        if not isinstance(self.verified_at, datetime):
            raise TypeError("verified_at must be a datetime.")

        if (
            self.verified_at.tzinfo is None
            or self.verified_at.utcoffset() is None
        ):
            raise ValueError("verified_at must be timezone-aware.")

        if self.execution_requested is not False:
            raise ValueError(
                "SignatureVerification must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "SignatureVerification must not permit side effects."
            )

    @staticmethod
    def _validate_digest(digest: str, field_name: str) -> None:
        if not isinstance(digest, str):
            raise TypeError(f"{field_name} must be a string.")

        prefix = "sha256:"
        if not digest.startswith(prefix):
            raise ValueError(f"{field_name} must use the sha256 prefix.")

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
                f"{field_name} must contain only lowercase hexadecimal characters."
            )

    @staticmethod
    def _require_non_empty(value: str, field_name: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")
        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")