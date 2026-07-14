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
from services.rollback_classifier import (
    RollbackClassificationError,
    RollbackClassifier,
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
    snapshot_id: str | None = None,
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
        snapshot_id=snapshot_id,
    )


def make_valid_rollback() -> tuple[ProcessEvent, ProcessEvent]:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-200",
        authority_role="PRIMARY",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.ROLLBACK,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="PRIMARY",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-200", "STATE-100"),
        evidence_ids=(
            "EVD-ROLLBACK-001",
            "EVD-SNAPSHOT-VERIFY-001",
            "EVD-TARGET-STATE-VERIFY-001",
            "EVD-AUTHORITY-PRESERVE-001",
        ),
        snapshot_id="SNAPSHOT-100",
    )
    return previous, current


def test_classifier_accepts_valid_rollback() -> None:
    previous, current = make_valid_rollback()

    result = RollbackClassifier().classify(previous, current)

    assert result.event_type is EventType.ROLLBACK
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.DEGRADED
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.RESTORED
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.ROLLED_BACK
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "RK-001" in result.applied_rules


def test_classifier_explains_valid_rollback() -> None:
    previous, current = make_valid_rollback()

    result = RollbackClassifier().classify(previous, current)

    assert any("rollback" in reason.lower() for reason in result.reasons)
    assert any("snapshot" in reason.lower() for reason in result.reasons)
    assert any("state" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_missing_rollback_evidence() -> None:
    previous, current = make_valid_rollback()

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
        snapshot_id=current.snapshot_id,
    )

    result = RollbackClassifier().classify(previous, unverified)

    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_lineage is LineageStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "RK-002" in result.applied_rules


def test_classifier_returns_hold_for_rollback_conflict() -> None:
    previous, current = make_valid_rollback()

    conflicted = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(
            "EVD-ROLLBACK-001",
            "EVD-SNAPSHOT-VERIFY-001",
            "EVD-TARGET-STATE-CONFLICT-001",
            "EVD-AUTHORITY-PRESERVE-001",
        ),
        snapshot_id=current.snapshot_id,
    )

    result = RollbackClassifier().classify(previous, conflicted)

    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_lineage is LineageStatus.CONFLICTED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.CONFLICTED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "RK-003" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_rollback()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.RESTORE,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        snapshot_id=current.snapshot_id,
    )

    with pytest.raises(RollbackClassificationError, match="ROLLBACK"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_unchanged_state_identity() -> None:
    previous, current = make_valid_rollback()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=previous.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        snapshot_id=current.snapshot_id,
    )

    with pytest.raises(RollbackClassificationError, match="(?i)state"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_runtime_identity() -> None:
    previous, current = make_valid_rollback()

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
        snapshot_id=current.snapshot_id,
    )

    with pytest.raises(RollbackClassificationError, match="(?i)runtime"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_execution_identity() -> None:
    previous, current = make_valid_rollback()

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
        snapshot_id=current.snapshot_id,
    )

    with pytest.raises(RollbackClassificationError, match="(?i)execution"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_service_identity() -> None:
    previous, current = make_valid_rollback()

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
        snapshot_id=current.snapshot_id,
        service_id="SERVICE-B",
    )

    with pytest.raises(RollbackClassificationError, match="(?i)service"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_authority_role() -> None:
    previous, current = make_valid_rollback()

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
        snapshot_id=current.snapshot_id,
    )

    with pytest.raises(RollbackClassificationError, match="(?i)authority"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_rollback()

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
        snapshot_id=current.snapshot_id,
    )

    with pytest.raises(RollbackClassificationError, match="(?i)parent"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_snapshot() -> None:
    previous, current = make_valid_rollback()

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
    )

    with pytest.raises(RollbackClassificationError, match="(?i)snapshot"):
        RollbackClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_rollback()

    with pytest.raises(TypeError, match="ProcessEvent"):
        RollbackClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )