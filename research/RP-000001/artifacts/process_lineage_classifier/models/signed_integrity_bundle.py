from dataclasses import dataclass
from datetime import datetime

from .detached_signature import DetachedSignature
from .recovery_integrity_bundle import RecoveryIntegrityBundle
from .signature_verification import SignatureVerification
from .signing_key_identity import SigningKeyIdentity


@dataclass(frozen=True, slots=True)
class SignedIntegrityBundle:
    """Immutable observer-only signed recovery integrity bundle."""

    signed_bundle_id: str

    bundle: RecoveryIntegrityBundle
    bundle_digest: str

    signature: DetachedSignature
    signing_key: SigningKeyIdentity
    verification: SignatureVerification

    created_at: datetime
    issuer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(
            self.signed_bundle_id,
            "signed_bundle_id",
        )
        self._require_non_empty(
            self.issuer_id,
            "issuer_id",
        )

        if not isinstance(
            self.bundle,
            RecoveryIntegrityBundle,
        ):
            raise TypeError(
                "bundle must be a RecoveryIntegrityBundle."
            )

        if not isinstance(
            self.signature,
            DetachedSignature,
        ):
            raise TypeError(
                "signature must be a DetachedSignature."
            )

        if not isinstance(
            self.signing_key,
            SigningKeyIdentity,
        ):
            raise TypeError(
                "signing_key must be a SigningKeyIdentity."
            )

        if not isinstance(
            self.verification,
            SignatureVerification,
        ):
            raise TypeError(
                "verification must be a SignatureVerification."
            )

        self._validate_digest(
            self.bundle_digest,
            "bundle_digest",
        )

        if self.verification.verified is not True:
            raise ValueError(
                "SignedIntegrityBundle requires a verified signature."
            )

        if not isinstance(self.created_at, datetime):
            raise TypeError(
                "created_at must be a datetime."
            )

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise ValueError(
                "created_at must be timezone-aware."
            )

        if self.created_at < self.verification.verified_at:
            raise ValueError(
                "Signed integrity bundle cannot be created before "
                "verification."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "SignedIntegrityBundle must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "SignedIntegrityBundle must not permit side effects."
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