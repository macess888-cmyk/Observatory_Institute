from datetime import datetime

from models import (
    RecoveryDecisionVerification,
    RecoveryVerificationReceipt,
)


class RecoveryVerificationReceiptError(ValueError):
    """Raised when a recovery verification receipt cannot be generated."""


class RecoveryVerificationReceiptService:
    """Generates immutable receipts for verified recovery replays."""

    def generate(
        self,
        *,
        receipt_id: str,
        verification: RecoveryDecisionVerification,
        replay_manifest_id: str,
        replay_manifest_digest: str,
        audit_chain_id: str,
        audit_root_digest: str,
        decision_digest: str,
        issued_at: datetime,
        issuer_id: str,
    ) -> RecoveryVerificationReceipt:
        if not isinstance(
            verification,
            RecoveryDecisionVerification,
        ):
            raise TypeError(
                "verification must be a RecoveryDecisionVerification."
            )

        self._require_non_empty(receipt_id, "receipt_id")
        self._require_non_empty(
            replay_manifest_id,
            "replay_manifest_id",
        )
        self._require_non_empty(
            audit_chain_id,
            "audit_chain_id",
        )
        self._require_non_empty(issuer_id, "issuer_id")

        self._validate_digest(
            replay_manifest_digest,
            "replay_manifest_digest",
        )
        self._validate_digest(
            audit_root_digest,
            "audit_root_digest",
        )
        self._validate_digest(
            decision_digest,
            "decision_digest",
        )
        self._validate_issue_time(
            issued_at,
            verification=verification,
        )

        if verification.verified is not True:
            raise RecoveryVerificationReceiptError(
                "Recovery verification receipt requires a verified result."
            )

        return RecoveryVerificationReceipt(
            receipt_id=receipt_id,
            verification_id=verification.verification_id,
            replay_id=verification.replay_id,
            original_decision_id=(
                verification.original_decision_id
            ),
            replay_manifest_id=replay_manifest_id,
            replay_manifest_digest=replay_manifest_digest,
            audit_chain_id=audit_chain_id,
            audit_root_digest=audit_root_digest,
            decision_digest=decision_digest,
            verified=True,
            issued_at=issued_at,
            issuer_id=issuer_id,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _validate_issue_time(
        issued_at: datetime,
        *,
        verification: RecoveryDecisionVerification,
    ) -> None:
        if not isinstance(issued_at, datetime):
            raise TypeError(
                "issued_at must be a datetime."
            )

        if (
            issued_at.tzinfo is None
            or issued_at.utcoffset() is None
        ):
            raise RecoveryVerificationReceiptError(
                "issued_at must be timezone-aware."
            )

        if issued_at < verification.verified_at:
            raise RecoveryVerificationReceiptError(
                "Receipt cannot be issued before verification."
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
            raise RecoveryVerificationReceiptError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise RecoveryVerificationReceiptError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise RecoveryVerificationReceiptError(
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
            raise RecoveryVerificationReceiptError(
                f"{field_name} must not be empty."
            )