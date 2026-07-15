from dataclasses import dataclass
from datetime import datetime

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)


@dataclass(frozen=True, slots=True)
class RecoveryAuditEvent:
    """Immutable observer-only event in a recovery audit trail."""

    event_id: str
    sequence_number: int
    event_type: str
    recovery_status: RecoveryDecisionStatus
    operational_status: OperationalStatus
    confidence: ConfidenceLevel
    occurred_at: datetime
    actor_id: str
    related_receipt_id: str | None
    evidence_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    conflicts: tuple[str, ...]
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.event_id, "event_id")
        self._require_non_empty(self.event_type, "event_type")
        self._require_non_empty(self.actor_id, "actor_id")

        if not isinstance(self.sequence_number, int):
            raise TypeError("sequence_number must be an integer.")

        if self.sequence_number < 1:
            raise ValueError("sequence_number must be greater than zero.")

        if not isinstance(self.recovery_status, RecoveryDecisionStatus):
            raise TypeError(
                "recovery_status must be a RecoveryDecisionStatus."
            )

        if not isinstance(self.operational_status, OperationalStatus):
            raise TypeError(
                "operational_status must be an OperationalStatus."
            )

        if not isinstance(self.confidence, ConfidenceLevel):
            raise TypeError("confidence must be a ConfidenceLevel.")

        if not isinstance(self.occurred_at, datetime):
            raise TypeError("occurred_at must be a datetime.")

        if (
            self.occurred_at.tzinfo is None
            or self.occurred_at.utcoffset() is None
        ):
            raise ValueError("occurred_at must be timezone-aware.")

        if (
            self.related_receipt_id is not None
            and not isinstance(self.related_receipt_id, str)
        ):
            raise TypeError(
                "related_receipt_id must be a string or None."
            )

        if (
            isinstance(self.related_receipt_id, str)
            and not self.related_receipt_id.strip()
        ):
            raise ValueError(
                "related_receipt_id must not be empty."
            )

        self._require_string_tuple(self.evidence_ids, "evidence_ids")
        self._require_string_tuple(self.reasons, "reasons")
        self._require_string_tuple(self.conflicts, "conflicts")

        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique.")

        self._validate_status_alignment()

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryAuditEvent must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryAuditEvent must not permit side effects."
            )

    def _validate_status_alignment(self) -> None:
        if (
            self.recovery_status
            is RecoveryDecisionStatus.RECOVERY_READY
            and self.operational_status
            is not OperationalStatus.PASS
        ):
            raise ValueError(
                "RECOVERY_READY requires OperationalStatus.PASS."
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
            raise TypeError(f"{field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")

    @staticmethod
    def _require_string_tuple(
        value: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(value, tuple):
            raise TypeError(f"{field_name} must be a tuple.")

        if any(not isinstance(item, str) for item in value):
            raise TypeError(
                f"{field_name} must contain only strings."
            )

        if any(not item.strip() for item in value):
            raise ValueError(
                f"{field_name} must not contain empty values."
            )