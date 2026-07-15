from datetime import datetime

from models import (
    ReconciliationReceipt,
    RecoveryAuditEvent,
)


class RecoveryAuditEventGenerationError(ValueError):
    """Raised when a recovery audit event cannot be generated."""

class RecoveryAuditEventService:
    """Generates immutable audit events from reconciliation receipts."""

    def generate(
        self,
        *,
        event_id: str,
        sequence_number: int,
        event_type: str,
        receipt: ReconciliationReceipt,
        occurred_at: datetime,
        actor_id: str,
    ) -> RecoveryAuditEvent:
        if not isinstance(receipt, ReconciliationReceipt):
            raise TypeError("receipt must be a ReconciliationReceipt.")

        self._require_non_empty(event_id, "event_id")
        self._require_non_empty(event_type, "event_type")
        self._require_non_empty(actor_id, "actor_id")
        self._validate_sequence_number(sequence_number)
        self._validate_occurred_at(occurred_at, receipt=receipt)

        return RecoveryAuditEvent(
            event_id=event_id,
            sequence_number=sequence_number,
            event_type=event_type,
            recovery_status=receipt.recovery_status,
            operational_status=receipt.operational_status,
            confidence=receipt.confidence,
            occurred_at=occurred_at,
            actor_id=actor_id,
            related_receipt_id=receipt.receipt_id,
            evidence_ids=receipt.evidence_ids,
            reasons=receipt.reasons,
            conflicts=receipt.conflicts,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _validate_sequence_number(sequence_number: int) -> None:
        if not isinstance(sequence_number, int):
            raise TypeError("sequence_number must be an integer.")
        if sequence_number < 1:
            raise RecoveryAuditEventGenerationError(
                "sequence_number must be greater than zero."
            )

    @staticmethod
    def _validate_occurred_at(
        occurred_at: datetime,
        *,
        receipt: ReconciliationReceipt,
    ) -> None:
        if not isinstance(occurred_at, datetime):
            raise TypeError("occurred_at must be a datetime.")
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise RecoveryAuditEventGenerationError(
                "occurred_at must be timezone-aware."
            )
        if occurred_at < receipt.issued_at:
            raise RecoveryAuditEventGenerationError(
                "Audit event cannot occur before the receipt issue time."
            )

    @staticmethod
    def _require_non_empty(value: str, field_name: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")
        if not value.strip():
            raise RecoveryAuditEventGenerationError(
                f"{field_name} must not be empty."
            )