from dataclasses import dataclass
from datetime import datetime

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)


@dataclass(frozen=True, slots=True)
class RecoveryDecisionReplay:
    """Immutable observer-only replay result for a recovery decision."""

    replay_id: str
    original_decision_id: str

    original_status: RecoveryDecisionStatus
    replayed_status: RecoveryDecisionStatus

    original_operational_status: OperationalStatus
    replayed_operational_status: OperationalStatus

    original_confidence: ConfidenceLevel
    replayed_confidence: ConfidenceLevel

    assessment_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    original_rules: tuple[str, ...]
    replayed_rules: tuple[str, ...]

    original_reasons: tuple[str, ...]
    replayed_reasons: tuple[str, ...]

    original_missing_evidence: tuple[str, ...]
    replayed_missing_evidence: tuple[str, ...]

    original_conflicts: tuple[str, ...]
    replayed_conflicts: tuple[str, ...]

    status_match: bool
    operational_status_match: bool
    confidence_match: bool
    rules_match: bool
    reasons_match: bool
    missing_evidence_match: bool
    conflicts_match: bool
    replay_verified: bool

    replayed_at: datetime
    replayer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.replay_id, "replay_id")
        self._require_non_empty(
            self.original_decision_id,
            "original_decision_id",
        )
        self._require_non_empty(self.replayer_id, "replayer_id")

        for field_name, value in (
            ("original_status", self.original_status),
            ("replayed_status", self.replayed_status),
        ):
            if not isinstance(value, RecoveryDecisionStatus):
                raise TypeError(
                    f"{field_name} must be a RecoveryDecisionStatus."
                )

        for field_name, value in (
            (
                "original_operational_status",
                self.original_operational_status,
            ),
            (
                "replayed_operational_status",
                self.replayed_operational_status,
            ),
        ):
            if not isinstance(value, OperationalStatus):
                raise TypeError(
                    f"{field_name} must be an OperationalStatus."
                )

        for field_name, value in (
            ("original_confidence", self.original_confidence),
            ("replayed_confidence", self.replayed_confidence),
        ):
            if not isinstance(value, ConfidenceLevel):
                raise TypeError(
                    f"{field_name} must be a ConfidenceLevel."
                )

        for field_name, values in (
            ("assessment_ids", self.assessment_ids),
            ("evidence_ids", self.evidence_ids),
            ("original_rules", self.original_rules),
            ("replayed_rules", self.replayed_rules),
            ("original_reasons", self.original_reasons),
            ("replayed_reasons", self.replayed_reasons),
            (
                "original_missing_evidence",
                self.original_missing_evidence,
            ),
            (
                "replayed_missing_evidence",
                self.replayed_missing_evidence,
            ),
            ("original_conflicts", self.original_conflicts),
            ("replayed_conflicts", self.replayed_conflicts),
        ):
            self._require_string_tuple(values, field_name)

        if len(set(self.assessment_ids)) != len(self.assessment_ids):
            raise ValueError(
                "assessment_ids must be unique."
            )

        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError(
                "evidence_ids must be unique."
            )

        for field_name, value in (
            ("status_match", self.status_match),
            (
                "operational_status_match",
                self.operational_status_match,
            ),
            ("confidence_match", self.confidence_match),
            ("rules_match", self.rules_match),
            ("reasons_match", self.reasons_match),
            (
                "missing_evidence_match",
                self.missing_evidence_match,
            ),
            ("conflicts_match", self.conflicts_match),
            ("replay_verified", self.replay_verified),
        ):
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        expected_replay_verified = all(
            (
                self.status_match,
                self.operational_status_match,
                self.confidence_match,
                self.rules_match,
                self.reasons_match,
                self.missing_evidence_match,
                self.conflicts_match,
            )
        )

        if self.replay_verified is not expected_replay_verified:
            raise ValueError(
                "replay_verified must match all replay comparison results."
            )

        if not isinstance(self.replayed_at, datetime):
            raise TypeError(
                "replayed_at must be a datetime."
            )

        if (
            self.replayed_at.tzinfo is None
            or self.replayed_at.utcoffset() is None
        ):
            raise ValueError(
                "replayed_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryDecisionReplay must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryDecisionReplay must not permit side effects."
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

    @staticmethod
    def _require_string_tuple(
        value: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field_name} must be a tuple."
            )

        if any(
            not isinstance(item, str)
            for item in value
        ):
            raise TypeError(
                f"{field_name} must contain only strings."
            )

        if any(
            not item.strip()
            for item in value
        ):
            raise ValueError(
                f"{field_name} must not contain empty values."
            )