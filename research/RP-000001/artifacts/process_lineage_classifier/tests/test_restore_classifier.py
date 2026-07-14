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
from services.restore_classifier import (
    RestoreClassificationError,
    RestoreClassifier,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: EventType,
    runtime_id: str,
    execution_id: str,
    state_id: str,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    snapshot_id: str | None = None,
    service_id: str = "SERVICE-A",
    host_id: str = "HOST-001",
    address: str = "10.0.0.10",
    authority_role: str = "PRIMARY",
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
        snapshot_id=snapshot_id,
    )


def test_classifier_accepts_valid_restore() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    result = RestoreClassifier().classify(previous, current)

    assert result.event_type is EventType.RESTORE
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.TERMINATED
    assert result.execution_continuity is ContinuityStatus.TERMINATED
    assert (
        result.state_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert (
        result.availability_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert result.state_lineage is LineageStatus.RESTORED
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.RESTORED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "RT-001" in result.applied_rules


def test_classifier_explains_valid_restore() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    result = RestoreClassifier().classify(previous, current)

    assert any("runtime" in reason.lower() for reason in result.reasons)
    assert any("execution" in reason.lower() for reason in result.reasons)
    assert any("state" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTART,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="RESTORE"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_unchanged_runtime_identity() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="(?i)runtime"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_unchanged_execution_identity() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-001",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="(?i)execution"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_changed_service_identity() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
        service_id="SERVICE-A",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        service_id="SERVICE-B",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="(?i)service"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_missing_parent_link() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="(?i)parent"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_missing_snapshot() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-STATE-VERIFY-001",),
    )

    with pytest.raises(RestoreClassificationError, match="(?i)snapshot"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_missing_state_evidence() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="(?i)evidence"):
        RestoreClassifier().classify(previous, current)


def test_classifier_rejects_unrelated_parent_state() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-999",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-999",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(RestoreClassificationError, match="(?i)previous state"):
        RestoreClassifier().classify(previous, current)


def test_classifier_requires_process_event_inputs() -> None:
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-002",
        execution_id="EXEC-002",
        state_id="STATE-001",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001", "EVD-STATE-VERIFY-001"),
        snapshot_id="SNAPSHOT-001",
    )

    with pytest.raises(TypeError, match="ProcessEvent"):
        RestoreClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )