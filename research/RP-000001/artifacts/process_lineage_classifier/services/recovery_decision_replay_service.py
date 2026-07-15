from datetime import datetime

from models import (
    RecoveryDecision,
    RecoveryDecisionReplay,
)


class RecoveryDecisionReplayError(ValueError):
    """Raised when a recovery decision cannot be replayed."""


class RecoveryDecisionReplayService:
    """Replays an immutable recovery decision without side effects."""

    def replay(
        self,
        *,
        replay_id: str,
        original_decision_id: str,
        decision: RecoveryDecision,
        assessment_ids: tuple[str, ...],
        evidence_ids: tuple[str, ...],
        replayed_at: datetime,
        replayer_id: str,
    ) -> RecoveryDecisionReplay:
        if not isinstance(decision, RecoveryDecision):
            raise TypeError(
                "decision must be a RecoveryDecision."
            )

        self._require_non_empty(replay_id, "replay_id")
        self._require_non_empty(
            original_decision_id,
            "original_decision_id",
        )
        self._require_non_empty(replayer_id, "replayer_id")

        self._validate_references(
            assessment_ids=assessment_ids,
            evidence_ids=evidence_ids,
        )
        self._validate_replay_time(replayed_at)

        replayed_status = decision.status
        replayed_operational_status = decision.operational_status
        replayed_confidence = decision.confidence
        replayed_rules = tuple(decision.applied_rules)
        replayed_reasons = tuple(decision.reasons)
        replayed_missing_evidence = tuple(
            decision.missing_evidence
        )
        replayed_conflicts = tuple(decision.conflicts)

        status_match = replayed_status is decision.status
        operational_status_match = (
            replayed_operational_status
            is decision.operational_status
        )
        confidence_match = (
            replayed_confidence
            is decision.confidence
        )
        rules_match = (
            replayed_rules == decision.applied_rules
        )
        reasons_match = (
            replayed_reasons == decision.reasons
        )
        missing_evidence_match = (
            replayed_missing_evidence
            == decision.missing_evidence
        )
        conflicts_match = (
            replayed_conflicts == decision.conflicts
        )

        replay_verified = all(
            (
                status_match,
                operational_status_match,
                confidence_match,
                rules_match,
                reasons_match,
                missing_evidence_match,
                conflicts_match,
            )
        )

        return RecoveryDecisionReplay(
            replay_id=replay_id,
            original_decision_id=original_decision_id,
            original_status=decision.status,
            replayed_status=replayed_status,
            original_operational_status=(
                decision.operational_status
            ),
            replayed_operational_status=(
                replayed_operational_status
            ),
            original_confidence=decision.confidence,
            replayed_confidence=replayed_confidence,
            assessment_ids=assessment_ids,
            evidence_ids=evidence_ids,
            original_rules=decision.applied_rules,
            replayed_rules=replayed_rules,
            original_reasons=decision.reasons,
            replayed_reasons=replayed_reasons,
            original_missing_evidence=(
                decision.missing_evidence
            ),
            replayed_missing_evidence=(
                replayed_missing_evidence
            ),
            original_conflicts=decision.conflicts,
            replayed_conflicts=replayed_conflicts,
            status_match=status_match,
            operational_status_match=(
                operational_status_match
            ),
            confidence_match=confidence_match,
            rules_match=rules_match,
            reasons_match=reasons_match,
            missing_evidence_match=(
                missing_evidence_match
            ),
            conflicts_match=conflicts_match,
            replay_verified=replay_verified,
            replayed_at=replayed_at,
            replayer_id=replayer_id,
            execution_requested=False,
            side_effects_permitted=False,
        )

    def _validate_references(
        self,
        *,
        assessment_ids: tuple[str, ...],
        evidence_ids: tuple[str, ...],
    ) -> None:
        if not isinstance(assessment_ids, tuple):
            raise TypeError(
                "assessment_ids must be a tuple."
            )

        if not isinstance(evidence_ids, tuple):
            raise TypeError(
                "evidence_ids must be a tuple."
            )

        if not assessment_ids:
            raise RecoveryDecisionReplayError(
                "Replay requires assessment references."
            )

        if not evidence_ids:
            raise RecoveryDecisionReplayError(
                "Replay requires evidence references."
            )

        self._require_string_members(
            assessment_ids,
            "assessment_ids",
        )
        self._require_string_members(
            evidence_ids,
            "evidence_ids",
        )

        if (
            len(set(assessment_ids))
            != len(assessment_ids)
        ):
            raise RecoveryDecisionReplayError(
                "duplicate assessment reference detected."
            )

        if len(set(evidence_ids)) != len(evidence_ids):
            raise RecoveryDecisionReplayError(
                "duplicate evidence reference detected."
            )

    @staticmethod
    def _validate_replay_time(
        replayed_at: datetime,
    ) -> None:
        if not isinstance(replayed_at, datetime):
            raise TypeError(
                "replayed_at must be a datetime."
            )

        if (
            replayed_at.tzinfo is None
            or replayed_at.utcoffset() is None
        ):
            raise RecoveryDecisionReplayError(
                "replayed_at must be timezone-aware."
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
            raise RecoveryDecisionReplayError(
                f"{field_name} must not be empty."
            )

    @staticmethod
    def _require_string_members(
        values: tuple[str, ...],
        field_name: str,
    ) -> None:
        if any(
            not isinstance(value, str)
            for value in values
        ):
            raise TypeError(
                f"{field_name} must contain only strings."
            )

        if any(
            not value.strip()
            for value in values
        ):
            raise RecoveryDecisionReplayError(
                f"{field_name} must not contain empty values."
            )