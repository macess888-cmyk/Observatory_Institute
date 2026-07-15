from datetime import datetime

from enums import EventType, RecoveryDecisionStatus
from models import (
    ReconciliationReceipt,
    RecoveryDecision,
)


class ReconciliationReceiptGenerationError(ValueError):
    """Raised when a reconciliation receipt cannot be generated."""


class ReconciliationReceiptService:
    """Generates immutable observer-only reconciliation receipts."""

    REQUIRED_READY_ASSESSMENT_TYPES = (
        EventType.AUTHORITY_CONVERGENCE,
        EventType.LINEAGE_RECONCILIATION,
        EventType.ROLLBACK_RECOVERY,
    )

    def generate(
        self,
        *,
        receipt_id: str,
        decision: RecoveryDecision,
        assessment_types: tuple[EventType, ...],
        assessment_ids: tuple[str, ...],
        evidence_ids: tuple[str, ...],
        issued_at: datetime,
        issuer_id: str,
    ) -> ReconciliationReceipt:
        if not isinstance(decision, RecoveryDecision):
            raise TypeError(
                "decision must be a RecoveryDecision."
            )

        self._require_non_empty(receipt_id, "receipt_id")
        self._require_non_empty(issuer_id, "issuer_id")
        self._validate_issue_time(issued_at)

        self._validate_references(
            assessment_types=assessment_types,
            assessment_ids=assessment_ids,
            evidence_ids=evidence_ids,
        )

        if (
            decision.status
            is RecoveryDecisionStatus.RECOVERY_READY
        ):
            self._validate_ready_assessments(
                assessment_types
            )

        return ReconciliationReceipt(
            receipt_id=receipt_id,
            recovery_status=decision.status,
            operational_status=decision.operational_status,
            confidence=decision.confidence,
            assessment_types=assessment_types,
            assessment_ids=assessment_ids,
            evidence_ids=evidence_ids,
            applied_rules=decision.applied_rules,
            reasons=decision.reasons,
            missing_evidence=decision.missing_evidence,
            conflicts=decision.conflicts,
            issued_at=issued_at,
            issuer_id=issuer_id,
            execution_requested=False,
            side_effects_permitted=False,
        )

    def _validate_references(
        self,
        *,
        assessment_types: tuple[EventType, ...],
        assessment_ids: tuple[str, ...],
        evidence_ids: tuple[str, ...],
    ) -> None:
        if not isinstance(assessment_types, tuple):
            raise TypeError(
                "assessment_types must be a tuple."
            )

        if not isinstance(assessment_ids, tuple):
            raise TypeError(
                "assessment_ids must be a tuple."
            )

        if not isinstance(evidence_ids, tuple):
            raise TypeError(
                "evidence_ids must be a tuple."
            )

        if not assessment_types:
            raise ReconciliationReceiptGenerationError(
                "Receipt generation requires assessment types."
            )

        if not assessment_ids:
            raise ReconciliationReceiptGenerationError(
                "Receipt generation requires assessment identities."
            )

        if not evidence_ids:
            raise ReconciliationReceiptGenerationError(
                "Receipt generation requires evidence identities."
            )

        if any(
            not isinstance(event_type, EventType)
            for event_type in assessment_types
        ):
            raise TypeError(
                "assessment_types must contain only EventType values."
            )

        self._require_string_members(
            assessment_ids,
            "assessment_ids",
        )
        self._require_string_members(
            evidence_ids,
            "evidence_ids",
        )

        if len(assessment_types) != len(assessment_ids):
            raise ReconciliationReceiptGenerationError(
                "Assessment types and identities must have matching counts."
            )

        if (
            len(set(assessment_types))
            != len(assessment_types)
        ):
            raise ReconciliationReceiptGenerationError(
                "duplicate assessment type detected."
            )

        if (
            len(set(assessment_ids))
            != len(assessment_ids)
        ):
            raise ReconciliationReceiptGenerationError(
                "duplicate assessment identity detected."
            )

        if len(set(evidence_ids)) != len(evidence_ids):
            raise ReconciliationReceiptGenerationError(
                "duplicate evidence identity detected."
            )

    def _validate_ready_assessments(
        self,
        assessment_types: tuple[EventType, ...],
    ) -> None:
        missing_required = tuple(
            event_type
            for event_type
            in self.REQUIRED_READY_ASSESSMENT_TYPES
            if event_type not in assessment_types
        )

        if missing_required:
            raise ReconciliationReceiptGenerationError(
                "RECOVERY_READY receipt is missing a required assessment."
            )

    @staticmethod
    def _validate_issue_time(
        issued_at: datetime,
    ) -> None:
        if not isinstance(issued_at, datetime):
            raise TypeError(
                "issued_at must be a datetime."
            )

        if (
            issued_at.tzinfo is None
            or issued_at.utcoffset() is None
        ):
            raise ReconciliationReceiptGenerationError(
                "issued_at must be timezone-aware."
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
            raise ReconciliationReceiptGenerationError(
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
            raise ReconciliationReceiptGenerationError(
                f"{field_name} must not contain empty values."
            )