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
from services.rebinding_classifier import (
    RebindingClassificationError,
    RebindingClassifier,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: EventType,
    runtime_id: str,
    execution_id: str,
    state_id: str,
    host_id: str,
    address: str,
    authority_role: str = "PRIMARY",
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    service_id: str = "SERVICE-A",
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


def make_valid_rebinding() -> tuple[ProcessEvent, ProcessEvent]:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        host_id="HOST-A",
        address="service-a.internal",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.REBIND,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        host_id="HOST-B",
        address="service-a.example.com",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-REBINDING-001",
            "EVD-TARGET-RESOLUTION-001",
            "EVD-OLD-BINDING-RELEASE-001",
        ),
    )
    return previous, current


def test_classifier_accepts_valid_rebinding() -> None:
    previous, current = make_valid_rebinding()

    result = RebindingClassifier().classify(previous, current)

    assert result.event_type is EventType.REBIND
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.REBOUND
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "RB-001" in result.applied_rules


def test_classifier_explains_valid_rebinding() -> None:
    previous, current = make_valid_rebinding()

    result = RebindingClassifier().classify(previous, current)

    assert any("binding" in reason.lower() for reason in result.reasons)
    assert any("address" in reason.lower() for reason in result.reasons)
    assert any("runtime" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_missing_rebinding_evidence() -> None:
    previous, current = make_valid_rebinding()

    unverified = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(),
    )

    result = RebindingClassifier().classify(previous, unverified)

    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "RB-002" in result.applied_rules


def test_classifier_returns_hold_for_binding_collision() -> None:
    previous, current = make_valid_rebinding()

    conflicted = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(
            "EVD-REBINDING-001",
            "EVD-TARGET-RESOLUTION-001",
            "EVD-BINDING-COLLISION-001",
        ),
    )

    result = RebindingClassifier().classify(previous, conflicted)

    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "RB-003" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.ADDRESS_CHANGE,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(RebindingClassificationError, match="REBIND"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_rejects_unchanged_address() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=previous.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(RebindingClassificationError, match="(?i)address"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_runtime_identity() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id="RUNTIME-B",
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(RebindingClassificationError, match="(?i)runtime"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_execution_identity() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id="EXEC-B",
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(RebindingClassificationError, match="(?i)execution"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_state_identity() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id="STATE-101",
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(RebindingClassificationError, match="(?i)state"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_service_identity() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        service_id="SERVICE-B",
    )

    with pytest.raises(RebindingClassificationError, match="(?i)service"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_rebinding()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        host_id=current.host_id,
        address=current.address,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(RebindingClassificationError, match="(?i)parent"):
        RebindingClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_rebinding()

    with pytest.raises(TypeError, match="ProcessEvent"):
        RebindingClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )