from datetime import datetime, timedelta, timezone

import pytest

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import RecoveryAuditEvent, RecoveryAuditTrail


BASE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: str,
    recovery_status: RecoveryDecisionStatus,
    operational_status: OperationalStatus,
    confidence: ConfidenceLevel,
    occurred_at: datetime,
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
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            occurred_at=BASE_TIME,
            evidence_ids=("EVD-001",),
        ),
        make_event(
            event_id="AUD-002",
            sequence_number=2,
            event_type="RECOVERY_ASSESSMENT_COMPLETED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            occurred_at=BASE_TIME + timedelta(seconds=1),
            related_receipt_id="RCP-001",
            evidence_ids=("EVD-002",),
        ),
    )

    return RecoveryAuditTrail(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )


def test_trail_accepts_ordered_audit_events() -> None:
    trail = make_valid_trail()

    assert trail.trail_id == "RAT-001"
    assert trail.subject_id == "RECOVERY-001"
    assert len(trail.events) == 2
    assert trail.events[0].sequence_number == 1
    assert trail.events[1].sequence_number == 2
    assert trail.execution_requested is False
    assert trail.side_effects_permitted is False


def test_trail_is_immutable() -> None:
    trail = make_valid_trail()

    with pytest.raises((AttributeError, TypeError)):
        trail.trail_id = "RAT-002"  # type: ignore[misc]


def test_event_is_immutable() -> None:
    event = make_valid_trail().events[0]

    with pytest.raises((AttributeError, TypeError)):
        event.event_id = "AUD-999"  # type: ignore[misc]


def test_trail_rejects_empty_trail_id() -> None:
    valid = make_valid_trail()

    with pytest.raises(ValueError, match="trail_id"):
        RecoveryAuditTrail(
            trail_id="",
            subject_id=valid.subject_id,
            events=valid.events,
            created_at=valid.created_at,
            issuer_id=valid.issuer_id,
        )


def test_trail_rejects_empty_subject_id() -> None:
    valid = make_valid_trail()

    with pytest.raises(ValueError, match="subject_id"):
        RecoveryAuditTrail(
            trail_id=valid.trail_id,
            subject_id="",
            events=valid.events,
            created_at=valid.created_at,
            issuer_id=valid.issuer_id,
        )


def test_trail_rejects_empty_event_set() -> None:
    with pytest.raises(ValueError, match="events"):
        RecoveryAuditTrail(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(),
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_trail_rejects_non_event_member() -> None:
    event = make_valid_trail().events[0]

    with pytest.raises(TypeError, match="RecoveryAuditEvent"):
        RecoveryAuditTrail(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(event, "AUD-002"),  # type: ignore[arg-type]
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_trail_rejects_duplicate_event_identity() -> None:
    first = make_valid_trail().events[0]
    duplicate = make_event(
        event_id=first.event_id,
        sequence_number=2,
        event_type="RECOVERY_ASSESSMENT_COMPLETED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        occurred_at=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(ValueError, match="event identity"):
        RecoveryAuditTrail(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, duplicate),
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_trail_rejects_duplicate_sequence_number() -> None:
    first = make_valid_trail().events[0]
    duplicate = make_event(
        event_id="AUD-002",
        sequence_number=first.sequence_number,
        event_type="RECOVERY_ASSESSMENT_COMPLETED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        occurred_at=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(ValueError, match="sequence"):
        RecoveryAuditTrail(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, duplicate),
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_trail_rejects_non_increasing_sequence() -> None:
    first = make_event(
        event_id="AUD-001",
        sequence_number=2,
        event_type="RECOVERY_ASSESSMENT_STARTED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        occurred_at=BASE_TIME,
    )
    second = make_event(
        event_id="AUD-002",
        sequence_number=1,
        event_type="RECOVERY_ASSESSMENT_COMPLETED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        occurred_at=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(ValueError, match="sequence"):
        RecoveryAuditTrail(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, second),
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_trail_rejects_non_increasing_timestamp() -> None:
    first = make_event(
        event_id="AUD-001",
        sequence_number=1,
        event_type="RECOVERY_ASSESSMENT_STARTED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        occurred_at=BASE_TIME + timedelta(seconds=1),
    )
    second = make_event(
        event_id="AUD-002",
        sequence_number=2,
        event_type="RECOVERY_ASSESSMENT_COMPLETED",
        recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        occurred_at=BASE_TIME,
    )

    with pytest.raises(ValueError, match="timestamp"):
        RecoveryAuditTrail(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, second),
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_event_rejects_ready_with_hold_status() -> None:
    with pytest.raises(ValueError, match="RECOVERY_READY"):
        make_event(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECOVERY_ASSESSMENT_COMPLETED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.HIGH,
            occurred_at=BASE_TIME,
        )


def test_event_rejects_hold_with_pass_status() -> None:
    with pytest.raises(ValueError, match="RECOVERY_HOLD"):
        make_event(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.LOW,
            occurred_at=BASE_TIME,
        )


def test_event_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_event(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            occurred_at=datetime(2026, 7, 14, 12, 0),
        )


def test_trail_rejects_naive_created_at() -> None:
    valid = make_valid_trail()

    with pytest.raises(ValueError, match="timezone-aware"):
        RecoveryAuditTrail(
            trail_id=valid.trail_id,
            subject_id=valid.subject_id,
            events=valid.events,
            created_at=datetime(2026, 7, 14, 12, 0),
            issuer_id=valid.issuer_id,
        )


def test_event_rejects_execution_request() -> None:
    with pytest.raises(ValueError, match="observer-only"):
        RecoveryAuditEvent(
            event_id="AUD-001",
            sequence_number=1,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            occurred_at=BASE_TIME,
            actor_id="PROCESS-LINEAGE-CLASSIFIER",
            related_receipt_id=None,
            evidence_ids=(),
            reasons=("Audit event recorded.",),
            conflicts=(),
            execution_requested=True,
            side_effects_permitted=False,
        )


def test_trail_rejects_side_effect_permission() -> None:
    valid = make_valid_trail()

    with pytest.raises(ValueError, match="side effects"):
        RecoveryAuditTrail(
            trail_id=valid.trail_id,
            subject_id=valid.subject_id,
            events=valid.events,
            created_at=valid.created_at,
            issuer_id=valid.issuer_id,
            side_effects_permitted=True,
        )