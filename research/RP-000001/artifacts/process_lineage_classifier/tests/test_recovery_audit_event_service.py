from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import (
    ReconciliationReceipt,
    RecoveryAuditEvent,
)
from services.recovery_audit_event_service import (
    RecoveryAuditEventGenerationError,
    RecoveryAuditEventService,
)


OCCURRED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_receipt(
    *,
    receipt_id: str = "RCP-001",
    recovery_status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    evidence_ids: tuple[str, ...] = (
        "EVD-QUORUM-001",
        "EVD-LINEAGE-001",
        "EVD-INTEGRITY-001",
    ),
    reasons: tuple[str, ...] = (
        "All required recovery assessments passed.",
    ),
    conflicts: tuple[str, ...] = (),
) -> ReconciliationReceipt:
    from enums import EventType

    return ReconciliationReceipt(
        receipt_id=receipt_id,
        recovery_status=recovery_status,
        operational_status=operational_status,
        confidence=confidence,
        assessment_types=(
            EventType.AUTHORITY_CONVERGENCE,
            EventType.LINEAGE_RECONCILIATION,
            EventType.ROLLBACK_RECOVERY,
        ),
        assessment_ids=(
            "AUTHORITY-CONVERGENCE:001",
            "LINEAGE-RECONCILIATION:001",
            "ROLLBACK-RECOVERY:001",
        ),
        evidence_ids=evidence_ids,
        applied_rules=("RO-001",),
        reasons=reasons,
        missing_evidence=(),
        conflicts=conflicts,
        issued_at=OCCURRED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_generates_ready_audit_event() -> None:
    receipt = make_receipt()

    event = RecoveryAuditEventService().generate(
        event_id="AUD-001",
        sequence_number=1,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        receipt=receipt,
        occurred_at=OCCURRED_AT,
        actor_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert isinstance(event, RecoveryAuditEvent)
    assert event.event_id == "AUD-001"
    assert event.sequence_number == 1
    assert event.event_type == "RECONCILIATION_RECEIPT_ISSUED"
    assert (
        event.recovery_status
        is RecoveryDecisionStatus.RECOVERY_READY
    )
    assert event.operational_status is OperationalStatus.PASS
    assert event.confidence is ConfidenceLevel.HIGH
    assert event.related_receipt_id == "RCP-001"
    assert event.evidence_ids == receipt.evidence_ids
    assert event.reasons == receipt.reasons
    assert event.conflicts == ()
    assert event.execution_requested is False
    assert event.side_effects_permitted is False


def test_service_generates_held_audit_event() -> None:
    receipt = make_receipt(
        receipt_id="RCP-002",
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        reasons=("Recovery remains held.",),
        conflicts=("Authority conflict remains.",),
    )

    event = RecoveryAuditEventService().generate(
        event_id="AUD-002",
        sequence_number=2,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        receipt=receipt,
        occurred_at=OCCURRED_AT,
        actor_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert (
        event.recovery_status
        is RecoveryDecisionStatus.RECOVERY_HOLD
    )
    assert event.operational_status is OperationalStatus.HOLD
    assert event.confidence is ConfidenceLevel.LOW
    assert event.related_receipt_id == "RCP-002"
    assert event.reasons == ("Recovery remains held.",)
    assert event.conflicts == ("Authority conflict remains.",)


def test_service_preserves_receipt_evidence() -> None:
    receipt = make_receipt()

    event = RecoveryAuditEventService().generate(
        event_id="AUD-001",
        sequence_number=1,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        receipt=receipt,
        occurred_at=OCCURRED_AT,
        actor_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert event.evidence_ids == receipt.evidence_ids


def test_service_rejects_non_receipt_input() -> None:
    with pytest.raises(TypeError, match="ReconciliationReceipt"):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt="RCP-001",  # type: ignore[arg-type]
            occurred_at=OCCURRED_AT,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_event_id() -> None:
    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="event_id",
    ):
        RecoveryAuditEventService().generate(
            event_id="",
            sequence_number=1,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=make_receipt(),
            occurred_at=OCCURRED_AT,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_event_type() -> None:
    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="event_type",
    ):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=1,
            event_type="",
            receipt=make_receipt(),
            occurred_at=OCCURRED_AT,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_actor_id() -> None:
    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="actor_id",
    ):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=make_receipt(),
            occurred_at=OCCURRED_AT,
            actor_id="",
        )


def test_service_rejects_zero_sequence_number() -> None:
    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="sequence_number",
    ):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=0,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=make_receipt(),
            occurred_at=OCCURRED_AT,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_negative_sequence_number() -> None:
    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="sequence_number",
    ):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=-1,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=make_receipt(),
            occurred_at=OCCURRED_AT,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_integer_sequence_number() -> None:
    with pytest.raises(TypeError, match="sequence_number"):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number="1",  # type: ignore[arg-type]
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=make_receipt(),
            occurred_at=OCCURRED_AT,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_naive_occurred_at() -> None:
    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="timezone-aware",
    ):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=make_receipt(),
            occurred_at=datetime(2026, 7, 14, 12, 0),
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_event_before_receipt_issue_time() -> None:
    receipt = make_receipt()

    with pytest.raises(
        RecoveryAuditEventGenerationError,
        match="before",
    ):
        RecoveryAuditEventService().generate(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            receipt=receipt,
            occurred_at=datetime(
                2026,
                7,
                14,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            ),
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    RecoveryAuditEventService().generate(
        event_id="AUD-001",
        sequence_number=1,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        receipt=receipt,
        occurred_at=OCCURRED_AT,
        actor_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert receipt == original


def test_service_preserves_observer_only_boundary() -> None:
    event = RecoveryAuditEventService().generate(
        event_id="AUD-001",
        sequence_number=1,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        receipt=make_receipt(),
        occurred_at=OCCURRED_AT,
        actor_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert event.execution_requested is False
    assert event.side_effects_permitted is False