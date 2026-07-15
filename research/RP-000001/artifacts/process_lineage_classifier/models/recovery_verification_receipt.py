from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RecoveryVerificationReceipt:
    """Immutable observer-only receipt for a verified recovery replay."""

    receipt_id: str
    verification_id: str
    replay_id: str
    original_decision_id: str

    replay_manifest_id: str
    replay_manifest_digest: str

    audit_chain_id: str
    audit_root_digest: str

    decision_digest: str
    verified: bool

    issued_at: datetime
    issuer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.receipt_id, "receipt_id")
        self._require_non_empty(
            self.verification_id,
            "verification_id",
        )
        self._require_non_empty(self.replay_id, "replay_id")
        self._require_non_empty(
            self.original_decision_id,
            "original_decision_id",
        )
        self._require_non_empty(
            self.replay_manifest_id,
            "replay_manifest_id",
        )
        self._require_non_empty(
            self.audit_chain_id,
            "audit_chain_id",
        )
        self._require_non_empty(self.issuer_id, "issuer_id")

        self._validate_digest(
            self.replay_manifest_digest,
            "replay_manifest_digest",
        )
        self._validate_digest(
            self.audit_root_digest,
            "audit_root_digest",
        )
        self._validate_digest(
            self.decision_digest,
            "decision_digest",
        )

        if not isinstance(self.verified, bool):
            raise TypeError("verified must be a boolean.")

        if self.verified is not True:
            raise ValueError(
                "RecoveryVerificationReceipt requires a verified result."
            )

        if not isinstance(self.issued_at, datetime):
            raise TypeError("issued_at must be a datetime.")

        if (
            self.issued_at.tzinfo is None
            or self.issued_at.utcoffset() is None
        ):
            raise ValueError(
                "issued_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryVerificationReceipt must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryVerificationReceipt must not permit side effects."
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