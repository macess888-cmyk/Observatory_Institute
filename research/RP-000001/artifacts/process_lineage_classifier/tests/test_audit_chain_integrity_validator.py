from datetime import datetime, timedelta, timezone

import pytest

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import (
    RecoveryAuditEvent,
    RecoveryAuditTrail,
)
from services.audit_chain_integrity_validator import (
    AuditChainIntegrityError,
    AuditChainIntegrityValidator,
)


BASE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    occurred_at: datetime,
    event_type: str,
    recovery_status: RecoveryDecisionStatus,
    operational_status: OperationalStatus,
    confidence: ConfidenceLevel,
    actor_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    related_receipt_id: str | None = None,
    evidence_ids: tuple[str, ...] = (),
    reasons: tuple[str, ...] = ("Audit event recorded.",),
    conflicts: tuple[str, ...] = (),
) -> RecoveryAuditEvent:
    return RecoveryAuditEvent(
        event_id=event_id,
        sequence_number=sequence_number,
        event_type=event_type,
        recovery_status=recovery_status,
        operational_status=operational_status,
        confidence=confidence,
        occurred_at=occurred_at,
        actor_id=actor_id,
        related_receipt_id=related_receipt_id,
        evidence_ids=evidence_ids,
        reasons=reasons,
        conflicts=conflicts,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_valid_trail() -> RecoveryAuditTrail:
    events = (
        make_event(
            event_id="AUD-001",
            sequence_number=1,
            occurred_at=BASE_TIME,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            evidence_ids=("EVD-START-001",),
        ),
        make_event(
            event_id="AUD-002",
            sequence_number=2,
            occurred_at=BASE_TIME + timedelta(seconds=1),
            event_type="RECOVERY_ASSESSMENT_COMPLETED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            evidence_ids=("EVD-COMPLETE-001",),
        ),
        make_event(
            event_id="AUD-003",
            sequence_number=3,
            occurred_at=BASE_TIME + timedelta(seconds=2),
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            related_receipt_id="RCP-001",
            evidence_ids=("EVD-RECEIPT-001",),
        ),
    )

    return RecoveryAuditTrail(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME + timedelta(seconds=3),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_audit_chain() -> None:
    trail = make_valid_trail()

    result = AuditChainIntegrityValidator().validate(trail)

    assert result is True


def test_validator_rejects_non_trail_input() -> None:
    with pytest.raises(TypeError, match="RecoveryAuditTrail"):
        AuditChainIntegrityValidator().validate(
            "RAT-001"  # type: ignore[arg-type]
        )


def test_validator_rejects_non_contiguous_sequence() -> None:
    first = make_event(
        event_id="AUD-001",
        sequence_number=1,
        occurred_at=BASE_TIME,
        event_type="RECOVERY_ASSESSMENT_STARTED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        evidence_ids=("EVD-START-001",),
    )
    second = make_event(
        event_id="AUD-002",
        sequence_number=3,
        occurred_at=BASE_TIME + timedelta(seconds=1),
        event_type="RECOVERY_ASSESSMENT_COMPLETED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        evidence_ids=("EVD-COMPLETE-001",),
    )
    third = make_event(
        event_id="AUD-003",
        sequence_number=4,
        occurred_at=BASE_TIME + timedelta(seconds=2),
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        related_receipt_id="RCP-001",
        evidence_ids=("EVD-RECEIPT-001",),
    )

    trail = RecoveryAuditTrail(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=(first, second, third),
        created_at=BASE_TIME + timedelta(seconds=3),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="contiguous",
    ):
        AuditChainIntegrityValidator().validate(trail)
def test_validator_rejects_sequence_not_starting_at_one() -> None:
    events = (
        make_event(
            event_id="AUD-001",
            sequence_number=2,
            occurred_at=BASE_TIME,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
        ),
        make_event(
            event_id="AUD-002",
            sequence_number=3,
            occurred_at=BASE_TIME + timedelta(seconds=1),
            event_type="RECOVERY_ASSESSMENT_COMPLETED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
        ),
    )

    trail = RecoveryAuditTrail(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME + timedelta(seconds=2),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="start at one",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_rejects_duplicate_evidence_across_chain() -> None:
    valid = make_valid_trail()
    first, second, third = valid.events

    duplicate_evidence_event = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        occurred_at=third.occurred_at,
        event_type=third.event_type,
        recovery_status=third.recovery_status,
        operational_status=third.operational_status,
        confidence=third.confidence,
        related_receipt_id=third.related_receipt_id,
        evidence_ids=("EVD-START-001",),
    )

    trail = RecoveryAuditTrail(
        trail_id=valid.trail_id,
        subject_id=valid.subject_id,
        events=(first, second, duplicate_evidence_event),
        created_at=valid.created_at,
        issuer_id=valid.issuer_id,
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="duplicate evidence",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_rejects_receipt_event_without_receipt_identity() -> None:
    valid = make_valid_trail()
    first, second, third = valid.events

    invalid_receipt_event = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        occurred_at=third.occurred_at,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        recovery_status=third.recovery_status,
        operational_status=third.operational_status,
        confidence=third.confidence,
        related_receipt_id=None,
        evidence_ids=third.evidence_ids,
    )

    trail = RecoveryAuditTrail(
        trail_id=valid.trail_id,
        subject_id=valid.subject_id,
        events=(first, second, invalid_receipt_event),
        created_at=valid.created_at,
        issuer_id=valid.issuer_id,
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="receipt identity",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_rejects_receipt_identity_on_non_receipt_event() -> None:
    valid = make_valid_trail()
    first, second, third = valid.events

    invalid_start_event = make_event(
        event_id=first.event_id,
        sequence_number=first.sequence_number,
        occurred_at=first.occurred_at,
        event_type=first.event_type,
        recovery_status=first.recovery_status,
        operational_status=first.operational_status,
        confidence=first.confidence,
        related_receipt_id="RCP-999",
        evidence_ids=first.evidence_ids,
    )

    trail = RecoveryAuditTrail(
        trail_id=valid.trail_id,
        subject_id=valid.subject_id,
        events=(invalid_start_event, second, third),
        created_at=valid.created_at,
        issuer_id=valid.issuer_id,
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="unexpected receipt",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_rejects_multiple_receipt_events() -> None:
    valid = make_valid_trail()
    first, second, third = valid.events

    second_receipt = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        occurred_at=second.occurred_at,
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        related_receipt_id="RCP-002",
        evidence_ids=second.evidence_ids,
    )

    trail = RecoveryAuditTrail(
        trail_id=valid.trail_id,
        subject_id=valid.subject_id,
        events=(first, second_receipt, third),
        created_at=valid.created_at,
        issuer_id=valid.issuer_id,
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="one receipt",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_rejects_receipt_event_before_final_position() -> None:
    first = make_event(
        event_id="AUD-001",
        sequence_number=1,
        occurred_at=BASE_TIME,
        event_type="RECOVERY_ASSESSMENT_STARTED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        evidence_ids=("EVD-START-001",),
    )
    receipt_event = make_event(
        event_id="AUD-002",
        sequence_number=2,
        occurred_at=BASE_TIME + timedelta(seconds=1),
        event_type="RECONCILIATION_RECEIPT_ISSUED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        related_receipt_id="RCP-001",
        evidence_ids=("EVD-RECEIPT-001",),
    )
    final_event = make_event(
        event_id="AUD-003",
        sequence_number=3,
        occurred_at=BASE_TIME + timedelta(seconds=2),
        event_type="RECOVERY_ASSESSMENT_COMPLETED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        evidence_ids=("EVD-COMPLETE-001",),
    )

    trail = RecoveryAuditTrail(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=(first, receipt_event, final_event),
        created_at=BASE_TIME + timedelta(seconds=3),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="final chain position",
    ):
        AuditChainIntegrityValidator().validate(trail)
def test_validator_rejects_actor_mismatch() -> None:
    valid = make_valid_trail()
    first, second, third = valid.events

    invalid_actor_event = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        occurred_at=second.occurred_at,
        event_type=second.event_type,
        recovery_status=second.recovery_status,
        operational_status=second.operational_status,
        confidence=second.confidence,
        actor_id="OTHER-SYSTEM",
        evidence_ids=second.evidence_ids,
    )

    trail = RecoveryAuditTrail(
        trail_id=valid.trail_id,
        subject_id=valid.subject_id,
        events=(first, invalid_actor_event, third),
        created_at=valid.created_at,
        issuer_id=valid.issuer_id,
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="actor",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_rejects_terminal_status_regression() -> None:
    valid = make_valid_trail()
    first, second, third = valid.events

    regressed = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        occurred_at=third.occurred_at,
        event_type=third.event_type,
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        related_receipt_id=third.related_receipt_id,
        evidence_ids=third.evidence_ids,
    )

    trail = RecoveryAuditTrail(
        trail_id=valid.trail_id,
        subject_id=valid.subject_id,
        events=(first, second, regressed),
        created_at=valid.created_at,
        issuer_id=valid.issuer_id,
    )

    with pytest.raises(
        AuditChainIntegrityError,
        match="regression",
    ):
        AuditChainIntegrityValidator().validate(trail)


def test_validator_accepts_all_hold_chain() -> None:
    events = (
        make_event(
            event_id="AUD-001",
            sequence_number=1,
            occurred_at=BASE_TIME,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            evidence_ids=("EVD-001",),
        ),
        make_event(
            event_id="AUD-002",
            sequence_number=2,
            occurred_at=BASE_TIME + timedelta(seconds=1),
            event_type="RECONCILIATION_RECEIPT_ISSUED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            related_receipt_id="RCP-001",
            evidence_ids=("EVD-002",),
        ),
    )

    trail = RecoveryAuditTrail(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME + timedelta(seconds=2),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert AuditChainIntegrityValidator().validate(trail) is True


def test_validator_does_not_mutate_trail() -> None:
    trail = make_valid_trail()
    original = trail

    AuditChainIntegrityValidator().validate(trail)

    assert trail == original


def test_validator_preserves_observer_only_boundary() -> None:
    trail = make_valid_trail()

    assert trail.execution_requested is False
    assert trail.side_effects_permitted is False
    assert AuditChainIntegrityValidator().validate(trail) is True
