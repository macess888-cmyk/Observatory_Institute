from dataclasses import dataclass
from datetime import datetime

from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)


@dataclass(frozen=True, slots=True)
class ReconciliationReceipt:
    """Immutable observer-only receipt for a recovery decision."""

    receipt_id: str
    recovery_status: RecoveryDecisionStatus
    operational_status: OperationalStatus
    confidence: ConfidenceLevel
    assessment_types: tuple[EventType, ...]
    assessment_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    applied_rules: tuple[str, ...]
    reasons: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    conflicts: tuple[str, ...]
    issued_at: datetime
    issuer_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.receipt_id, "receipt_id")
        self._require_non_empty(self.issuer_id, "issuer_id")

        if not isinstance(
            self.recovery_status,
            RecoveryDecisionStatus,
        ):
            raise TypeError(
                "recovery_status must be a RecoveryDecisionStatus."
            )

        if not isinstance(
            self.operational_status,
            OperationalStatus,
        ):
            raise TypeError(
                "operational_status must be an OperationalStatus."
            )

        if not isinstance(self.confidence, ConfidenceLevel):
            raise TypeError(
                "confidence must be a ConfidenceLevel."
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

        self._require_tuple(
            self.assessment_types,
            "assessment_types",
        )
        self._require_string_tuple(
            self.assessment_ids,
            "assessment_ids",
        )
        self._require_string_tuple(
            self.evidence_ids,
            "evidence_ids",
        )
        self._require_string_tuple(
            self.applied_rules,
            "applied_rules",
        )
        self._require_string_tuple(
            self.reasons,
            "reasons",
        )
        self._require_string_tuple(
            self.missing_evidence,
            "missing_evidence",
        )
        self._require_string_tuple(
            self.conflicts,
            "conflicts",
        )

        if any(
            not isinstance(event_type, EventType)
            for event_type in self.assessment_types
        ):
            raise TypeError(
                "assessment_types must contain only EventType values."
            )

        if (
            len(set(self.assessment_types))
            != len(self.assessment_types)
        ):
            raise ValueError(
                "assessment_types must be unique."
            )

        if (
            len(set(self.assessment_ids))
            != len(self.assessment_ids)
        ):
            raise ValueError(
                "assessment_ids must be unique."
            )

        if len(self.assessment_types) != len(self.assessment_ids):
            raise ValueError(
                "assessment_types and assessment_ids must have "
                "matching assessment counts."
            )

        if (
            len(set(self.evidence_ids))
            != len(self.evidence_ids)
        ):
            raise ValueError(
                "evidence_ids must be unique."
            )

        self._validate_status_alignment()

        if self.execution_requested is not False:
            raise ValueError(
                "ReconciliationReceipt must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "ReconciliationReceipt must not permit side effects."
            )

    def _validate_status_alignment(self) -> None:
        if (
            self.recovery_status
            is RecoveryDecisionStatus.RECOVERY_READY
        ):
            if self.operational_status is not OperationalStatus.PASS:
                raise ValueError(
                    "RECOVERY_READY requires OperationalStatus.PASS."
                )

            if self.missing_evidence:
                raise ValueError(
                    "RECOVERY_READY cannot contain missing evidence."
                )

            if self.conflicts:
                raise ValueError(
                    "RECOVERY_READY cannot contain conflicts."
                )

        if (
            self.recovery_status
            is RecoveryDecisionStatus.RECOVERY_HOLD
            and self.operational_status
            is not OperationalStatus.HOLD
        ):
            raise ValueError(
                "RECOVERY_HOLD requires OperationalStatus.HOLD."
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
    def _require_tuple(
        value: tuple[object, ...],
        field_name: str,
    ) -> None:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field_name} must be a tuple."
            )

    @classmethod
    def _require_string_tuple(
        cls,
        value: tuple[str, ...],
        field_name: str,
    ) -> None:
        cls._require_tuple(value, field_name)

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