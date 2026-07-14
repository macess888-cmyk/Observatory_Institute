from datetime import datetime, timedelta, timezone

import pytest

from enums import (
    BindingStatus,
    ConfidenceLevel,
    ConflictStatus,
    ContinuityStatus,
    EventType,
    LineageStatus,
    OperationalStatus,
    TransitionStatus,
)
from models import ProcessEvent
from services.termination_classifier import (
    TerminationClassificationError,
    TerminationClassifier,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: EventType,
    runtime_id: str,
    execution_id: str,
    state_id: str,
    authority_role: str,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    service_id: str = "SERVICE-A",
    host_id: str = "HOST-001",
    address: str = "10.0.0.10",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=event_type,
        timestamp=datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
        + timedelta(seconds=sequence_number),
        sequence_number=sequence_number,
        service_id=service_id,
        runtime_id=runtime_id,
        execution_id=execution_id,
        state_id=state_id,
        host_id=host_id,
        address=address,
        authority_role=authority_role,
        parent_event_ids=parent_event_ids,
        parent_state_ids=parent_state_ids,
        evidence_ids=evidence_ids,
    )


def make_valid_termination() -> tuple[ProcessEvent, ProcessEvent]:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="PRIMARY",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.TERMINATE,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="NONE",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-TERMINATION-001",
            "EVD-EXECUTION-STOP-001",
            "EVD-AUTHORITY-REVOCATION-001",
        ),
    )
    return previous, current


def test_classifier_accepts_valid_termination() -> None:
    previous, current = make_valid_termination()

    result = TerminationClassifier().classify(previous, current)

    assert result.event_type is EventType.TERMINATE
    assert result.service_continuity is ContinuityStatus.TERMINATED
    assert result.runtime_continuity is ContinuityStatus.TERMINATED
    assert result.execution_continuity is ContinuityStatus.TERMINATED
    assert result.state_continuity is ContinuityStatus.TERMINATED
    assert result.authority_continuity is ContinuityStatus.TERMINATED
    assert result.availability_continuity is ContinuityStatus.TERMINATED
    assert result.state_lineage is LineageStatus.DISCONTINUOUS
    assert result.binding_status is BindingStatus.EXPIRED
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.TERMINATED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "TM-001" in result.applied_rules


def test_classifier_explains_valid_termination() -> None:
    previous, current = make_valid_termination()

    result = TerminationClassifier().classify(previous, current)

    assert any("runtime" in reason.lower() for reason in result.reasons)
    assert any("execution" in reason.lower() for reason in result.reasons)
    assert any("authority" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_missing_termination_evidence() -> None:
    previous, current = make_valid_termination()

    unverified = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(),
    )

    result = TerminationClassifier().classify(previous, unverified)

    assert result.runtime_continuity is ContinuityStatus.UNVERIFIED
    assert result.execution_continuity is ContinuityStatus.UNVERIFIED
    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "TM-002" in result.applied_rules


def test_classifier_returns_hold_when_authority_remains_active() -> None:
    previous, current = make_valid_termination()

    conflicted = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role="PRIMARY",
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(
            "EVD-TERMINATION-001",
            "EVD-EXECUTION-STOP-001",
            "EVD-AUTHORITY-STILL-ACTIVE-001",
        ),
    )

    result = TerminationClassifier().classify(previous, conflicted)

    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "TM-003" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.DEMOTE,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(TerminationClassificationError, match="TERMINATE"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_runtime_identity() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id="RUNTIME-B",
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(TerminationClassificationError, match="(?i)runtime"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_execution_identity() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id="EXEC-B",
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(TerminationClassificationError, match="(?i)execution"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_state_identity() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id="STATE-101",
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(TerminationClassificationError, match="(?i)state"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_service_identity() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        service_id="SERVICE-B",
    )

    with pytest.raises(TerminationClassificationError, match="(?i)service"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(TerminationClassificationError, match="(?i)parent"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_rejects_invalid_terminated_role() -> None:
    previous, current = make_valid_termination()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role="SECONDARY",
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(TerminationClassificationError, match="(?i)NONE"):
        TerminationClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_termination()

    with pytest.raises(TypeError, match="ProcessEvent"):
        TerminationClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )