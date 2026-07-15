from datetime import datetime

from models import (
    RecoveryDecisionReplay,
    RecoveryDecisionVerification,
)


class RecoveryDecisionVerificationError(ValueError):
    """Raised when a recovery decision replay cannot be verified."""


class RecoveryDecisionVerifier:
    """Verifies an observer-only recovery decision replay."""

    def verify(
        self,
        *,
        verification_id: str,
        replay: RecoveryDecisionReplay,
        verified_at: datetime,
        verifier_id: str,
    ) -> RecoveryDecisionVerification:
        if not isinstance(replay, RecoveryDecisionReplay):
            raise TypeError(
                "replay must be a RecoveryDecisionReplay."
            )

        self._require_non_empty(
            verification_id,
            "verification_id",
        )
        self._require_non_empty(verifier_id, "verifier_id")
        self._validate_verification_time(
            verified_at,
            replay=replay,
        )
        self._validate_comparisons(replay)

        return RecoveryDecisionVerification(
            verification_id=verification_id,
            replay_id=replay.replay_id,
            original_decision_id=replay.original_decision_id,
            verified=True,
            replay_verified=replay.replay_verified,
            status_match=replay.status_match,
            operational_status_match=(
                replay.operational_status_match
            ),
            confidence_match=replay.confidence_match,
            rules_match=replay.rules_match,
            reasons_match=replay.reasons_match,
            missing_evidence_match=(
                replay.missing_evidence_match
            ),
            conflicts_match=replay.conflicts_match,
            verified_at=verified_at,
            verifier_id=verifier_id,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _validate_comparisons(
        replay: RecoveryDecisionReplay,
    ) -> None:
        if not replay.status_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains a status mismatch."
            )

        if not replay.operational_status_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains an operational "
                "status mismatch."
            )

        if not replay.confidence_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains a confidence mismatch."
            )

        if not replay.rules_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains a rules mismatch."
            )

        if not replay.reasons_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains a reasons mismatch."
            )

        if not replay.missing_evidence_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains a missing "
                "evidence mismatch."
            )

        if not replay.conflicts_match:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay contains a conflicts mismatch."
            )

        if not replay.replay_verified:
            raise RecoveryDecisionVerificationError(
                "Recovery decision replay is not verified."
            )

    @staticmethod
    def _validate_verification_time(
        verified_at: datetime,
        *,
        replay: RecoveryDecisionReplay,
    ) -> None:
        if not isinstance(verified_at, datetime):
            raise TypeError(
                "verified_at must be a datetime."
            )

        if (
            verified_at.tzinfo is None
            or verified_at.utcoffset() is None
        ):
            raise RecoveryDecisionVerificationError(
                "verified_at must be timezone-aware."
            )

        if verified_at < replay.replayed_at:
            raise RecoveryDecisionVerificationError(
                "Verification cannot occur before replay."
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
            raise RecoveryDecisionVerificationError(
                f"{field_name} must not be empty."
            )