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
from services.pause_classifier import (
    PauseClassificationError,
    PauseClassifier,
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


def make_valid_pause() -> tuple[ProcessEvent, ProcessEvent]:
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
        event_type=EventType.PAUSE,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="NONE",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-PAUSE-001",
            "EVD-EXECUTION-SUSPEND-001",
            "EVD-STATE-PRESERVE-001",
            "EVD-AUTHORITY-SUSPEND-001",
        ),
    )
    return previous, current


def test_classifier_accepts_valid_pause() -> None:
    previous, current = make_valid_pause()

    result = PauseClassifier().classify(previous, current)

    assert result.event_type is EventType.PAUSE
    assert result.service_continuity is ContinuityStatus.INTERRUPTED
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.INTERRUPTED
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.INTERRUPTED
    assert result.availability_continuity is ContinuityStatus.INTERRUPTED
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.SUSPENDED
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.PAUSED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "PS-001" in result.applied_rules


def test_classifier_explains_valid_pause() -> None:
    previous, current = make_valid_pause()

    result = PauseClassifier().classify(previous, current)

    assert any("runtime" in reason.lower() for reason in result.reasons)
    assert any("execution" in reason.lower() for reason in result.reasons)
    assert any("state" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_missing_pause_evidence() -> None:
    previous, current = make_valid_pause()

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

    result = PauseClassifier().classify(previous, unverified)

    assert result.execution_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "PS-002" in result.applied_rules


def test_classifier_returns_hold_when_authority_remains_active() -> None:
    previous, current = make_valid_pause()

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
            "EVD-PAUSE-001",
            "EVD-EXECUTION-SUSPEND-001",
            "EVD-STATE-PRESERVE-001",
            "EVD-AUTHORITY-STILL-ACTIVE-001",
        ),
    )

    result = PauseClassifier().classify(previous, conflicted)

    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "PS-003" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_pause()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.TERMINATE,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(PauseClassificationError, match="PAUSE"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_runtime_identity() -> None:
    previous, current = make_valid_pause()

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

    with pytest.raises(PauseClassificationError, match="(?i)runtime"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_execution_identity() -> None:
    previous, current = make_valid_pause()

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

    with pytest.raises(PauseClassificationError, match="(?i)execution"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_state_identity() -> None:
    previous, current = make_valid_pause()

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

    with pytest.raises(PauseClassificationError, match="(?i)state"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_service_identity() -> None:
    previous, current = make_valid_pause()

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

    with pytest.raises(PauseClassificationError, match="(?i)service"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_pause()

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

    with pytest.raises(PauseClassificationError, match="(?i)parent"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_rejects_invalid_paused_role() -> None:
    previous, current = make_valid_pause()

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

    with pytest.raises(PauseClassificationError, match="(?i)NONE"):
        PauseClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_pause()

    with pytest.raises(TypeError, match="ProcessEvent"):
        PauseClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )