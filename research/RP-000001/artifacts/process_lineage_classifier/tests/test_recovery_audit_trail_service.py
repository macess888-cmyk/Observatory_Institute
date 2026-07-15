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
from services.recovery_audit_trail_service import (
    RecoveryAuditTrailAssemblyError,
    RecoveryAuditTrailService,
)


BASE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    occurred_at: datetime,
    event_type: str = "RECONCILIATION_RECEIPT_ISSUED",
    recovery_status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    actor_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    related_receipt_id: str | None = "RCP-001",
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


def make_valid_events() -> tuple[RecoveryAuditEvent, ...]:
    return (
        make_event(
            event_id="AUD-001",
            sequence_number=1,
            occurred_at=BASE_TIME,
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            related_receipt_id=None,
            evidence_ids=("EVD-001",),
        ),
        make_event(
            event_id="AUD-002",
            sequence_number=2,
            occurred_at=BASE_TIME + timedelta(seconds=1),
            evidence_ids=("EVD-002",),
        ),
    )


def test_service_assembles_valid_audit_trail() -> None:
    events = make_valid_events()

    trail = RecoveryAuditTrailService().assemble(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME + timedelta(seconds=2),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert isinstance(trail, RecoveryAuditTrail)
    assert trail.trail_id == "RAT-001"
    assert trail.subject_id == "RECOVERY-001"
    assert trail.events == events
    assert trail.created_at == BASE_TIME + timedelta(seconds=2)
    assert trail.issuer_id == "PROCESS-LINEAGE-CLASSIFIER"
    assert trail.execution_requested is False
    assert trail.side_effects_permitted is False


def test_service_preserves_event_order() -> None:
    events = make_valid_events()

    trail = RecoveryAuditTrailService().assemble(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME + timedelta(seconds=2),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert trail.events[0].event_id == "AUD-001"
    assert trail.events[1].event_id == "AUD-002"


def test_service_rejects_empty_event_set() -> None:
    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="at least one",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(),
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_tuple_events() -> None:
    events = make_valid_events()

    with pytest.raises(TypeError, match="tuple"):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=list(events),  # type: ignore[arg-type]
            created_at=BASE_TIME + timedelta(seconds=2),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_audit_event_member() -> None:
    first, _ = make_valid_events()

    with pytest.raises(TypeError, match="RecoveryAuditEvent"):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, "AUD-002"),  # type: ignore[arg-type]
            created_at=BASE_TIME + timedelta(seconds=2),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_event_identity() -> None:
    first, second = make_valid_events()
    duplicate = make_event(
        event_id=first.event_id,
        sequence_number=second.sequence_number,
        occurred_at=second.occurred_at,
    )

    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="duplicate event identity",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, duplicate),
            created_at=BASE_TIME + timedelta(seconds=2),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_sequence_number() -> None:
    first, second = make_valid_events()
    duplicate = make_event(
        event_id=second.event_id,
        sequence_number=first.sequence_number,
        occurred_at=second.occurred_at,
    )

    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="duplicate sequence",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, duplicate),
            created_at=BASE_TIME + timedelta(seconds=2),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_increasing_sequence() -> None:
    first = make_event(
        event_id="AUD-001",
        sequence_number=2,
        occurred_at=BASE_TIME,
    )
    second = make_event(
        event_id="AUD-002",
        sequence_number=1,
        occurred_at=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="increasing sequence",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, second),
            created_at=BASE_TIME + timedelta(seconds=2),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_increasing_timestamps() -> None:
    first = make_event(
        event_id="AUD-001",
        sequence_number=1,
        occurred_at=BASE_TIME + timedelta(seconds=1),
    )
    second = make_event(
        event_id="AUD-002",
        sequence_number=2,
        occurred_at=BASE_TIME,
    )

    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="increasing timestamp",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=(first, second),
            created_at=BASE_TIME + timedelta(seconds=2),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_created_at_before_last_event() -> None:
    events = make_valid_events()

    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="last event",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=events,
            created_at=BASE_TIME,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_accepts_created_at_equal_to_last_event() -> None:
    events = make_valid_events()

    trail = RecoveryAuditTrailService().assemble(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=events[-1].occurred_at,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert trail.created_at == events[-1].occurred_at


def test_service_rejects_naive_created_at() -> None:
    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match="timezone-aware",
    ):
        RecoveryAuditTrailService().assemble(
            trail_id="RAT-001",
            subject_id="RECOVERY-001",
            events=make_valid_events(),
            created_at=datetime(2026, 7, 14, 12, 0),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("trail_id", ""),
        ("subject_id", ""),
        ("issuer_id", ""),
    ],
)
def test_service_rejects_empty_identity(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "trail_id": "RAT-001",
        "subject_id": "RECOVERY-001",
        "events": make_valid_events(),
        "created_at": BASE_TIME + timedelta(seconds=2),
        "issuer_id": "PROCESS-LINEAGE-CLASSIFIER",
    }
    arguments[field_name] = value

    with pytest.raises(
        RecoveryAuditTrailAssemblyError,
        match=field_name,
    ):
        RecoveryAuditTrailService().assemble(**arguments)


def test_service_does_not_mutate_events() -> None:
    events = make_valid_events()
    original = tuple(events)

    RecoveryAuditTrailService().assemble(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=events,
        created_at=BASE_TIME + timedelta(seconds=2),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert events == original


def test_service_preserves_observer_only_boundary() -> None:
    trail = RecoveryAuditTrailService().assemble(
        trail_id="RAT-001",
        subject_id="RECOVERY-001",
        events=make_valid_events(),
        created_at=BASE_TIME + timedelta(seconds=2),
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert trail.execution_requested is False
    assert trail.side_effects_permitted is False