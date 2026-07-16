from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class HistoricalSignatureVerificationReceipt:
    """Immutable observer-only receipt for historical signature verification."""

    receipt_id: str
    verification_id: str
    signature_id: str
    key_id: str

    subject_id: str
    subject_type: str

    content_digest: str
    payload_digest: str
    public_key_fingerprint: str

    algorithm: str
    signer_id: str
    verifier_id: str

    registry_id: str

    signing_registry_version: str
    signing_snapshot_id: str
    signing_snapshot_digest: str

    verification_registry_version: str
    verification_snapshot_id: str
    verification_snapshot_digest: str

    signed_at: datetime
    verified_at: datetime

    mathematical_verification: bool
    identity_match: bool
    content_match: bool
    signing_time_key_present: bool
    verification_time_key_present: bool
    key_valid_at_signing: bool

    verified: bool

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("receipt_id", self.receipt_id),
            ("verification_id", self.verification_id),
            ("signature_id", self.signature_id),
            ("key_id", self.key_id),
            ("subject_id", self.subject_id),
            ("subject_type", self.subject_type),
            ("algorithm", self.algorithm),
            ("signer_id", self.signer_id),
            ("verifier_id", self.verifier_id),
            ("registry_id", self.registry_id),
            (
                "signing_registry_version",
                self.signing_registry_version,
            ),
            (
                "signing_snapshot_id",
                self.signing_snapshot_id,
            ),
            (
                "verification_registry_version",
                self.verification_registry_version,
            ),
            (
                "verification_snapshot_id",
                self.verification_snapshot_id,
            ),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            self.content_digest,
            "content_digest",
        )
        self._validate_digest(
            self.payload_digest,
            "payload_digest",
        )
        self._validate_digest(
            self.public_key_fingerprint,
            "public_key_fingerprint",
        )
        self._validate_digest(
            self.signing_snapshot_digest,
            "signing_snapshot_digest",
        )
        self._validate_digest(
            self.verification_snapshot_digest,
            "verification_snapshot_digest",
        )

        if self.algorithm != "ED25519":
            raise ValueError(
                "algorithm must be ED25519."
            )

        self._validate_datetime(
            self.signed_at,
            "signed_at",
        )
        self._validate_datetime(
            self.verified_at,
            "verified_at",
        )

        if self.verified_at < self.signed_at:
            raise ValueError(
                "Verification cannot occur before signature creation."
            )

        for field_name, value in (
            (
                "mathematical_verification",
                self.mathematical_verification,
            ),
            ("identity_match", self.identity_match),
            ("content_match", self.content_match),
            (
                "signing_time_key_present",
                self.signing_time_key_present,
            ),
            (
                "verification_time_key_present",
                self.verification_time_key_present,
            ),
            (
                "key_valid_at_signing",
                self.key_valid_at_signing,
            ),
            ("verified", self.verified),
        ):
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        expected_verified = all(
            (
                self.mathematical_verification,
                self.identity_match,
                self.content_match,
                self.signing_time_key_present,
                self.key_valid_at_signing,
            )
        )

        if self.verified is not expected_verified:
            raise ValueError(
                "verified must match required verification components."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "HistoricalSignatureVerificationReceipt "
                "must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "HistoricalSignatureVerificationReceipt "
                "must not permit side effects."
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