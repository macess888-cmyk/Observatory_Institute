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
from services.clone_classifier import (
    CloneClassificationError,
    CloneClassifier,
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
    branch_id: str | None = None,
    service_id: str = "SERVICE-A",
    host_id: str = "HOST-001",
    address: str = "10.0.0.10",
    authority_role: str = "SECONDARY",
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
        branch_id=branch_id,
    )


def make_valid_clone_set() -> tuple[ProcessEvent, ProcessEvent, ProcessEvent]:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-PARENT",
        execution_id="EXEC-PARENT",
        state_id="STATE-001",
        authority_role="PRIMARY",
    )
    clone_a = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.CLONE,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
        host_id="HOST-A",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001",),
        snapshot_id="SNAPSHOT-001",
        branch_id="BRANCH-A",
    )
    clone_b = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.CLONE,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        host_id="HOST-B",
        address="10.0.0.30",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=("EVD-SNAPSHOT-001",),
        snapshot_id="SNAPSHOT-001",
        branch_id="BRANCH-B",
    )
    return parent, clone_a, clone_b


def test_classifier_accepts_valid_clone_pair() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    result = CloneClassifier().classify(parent, (clone_a, clone_b))

    assert result.event_type is EventType.CLONE
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.TERMINATED
    assert result.execution_continuity is ContinuityStatus.TERMINATED
    assert (
        result.state_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert (
        result.authority_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert (
        result.availability_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert result.state_lineage is LineageStatus.SHARED_PARENT
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.CLONED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "CL-001" in result.applied_rules


def test_classifier_explains_clone_pair() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    result = CloneClassifier().classify(parent, (clone_a, clone_b))

    assert any("distinct runtime" in reason.lower() for reason in result.reasons)
    assert any("shared parent" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_authority_collision() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    clone_a = make_event(
        event_id=clone_a.event_id,
        sequence_number=clone_a.sequence_number,
        event_type=clone_a.event_type,
        runtime_id=clone_a.runtime_id,
        execution_id=clone_a.execution_id,
        state_id=clone_a.state_id,
        host_id=clone_a.host_id,
        address=clone_a.address,
        parent_event_ids=clone_a.parent_event_ids,
        parent_state_ids=clone_a.parent_state_ids,
        evidence_ids=clone_a.evidence_ids,
        snapshot_id=clone_a.snapshot_id,
        branch_id=clone_a.branch_id,
        authority_role="PRIMARY",
    )
    clone_b = make_event(
        event_id=clone_b.event_id,
        sequence_number=clone_b.sequence_number,
        event_type=clone_b.event_type,
        runtime_id=clone_b.runtime_id,
        execution_id=clone_b.execution_id,
        state_id=clone_b.state_id,
        host_id=clone_b.host_id,
        address=clone_b.address,
        parent_event_ids=clone_b.parent_event_ids,
        parent_state_ids=clone_b.parent_state_ids,
        evidence_ids=clone_b.evidence_ids,
        snapshot_id=clone_b.snapshot_id,
        branch_id=clone_b.branch_id,
        authority_role="PRIMARY",
    )

    result = CloneClassifier().classify(parent, (clone_a, clone_b))

    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts


def test_classifier_rejects_single_clone_child() -> None:
    parent, clone_a, _ = make_valid_clone_set()

    with pytest.raises(CloneClassificationError, match="at least two"):
        CloneClassifier().classify(parent, (clone_a,))


def test_classifier_rejects_wrong_child_event_type() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    clone_b = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.RESTORE,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        snapshot_id="SNAPSHOT-001",
        branch_id="BRANCH-B",
    )

    with pytest.raises(CloneClassificationError, match="CLONE"):
        CloneClassifier().classify(parent, (clone_a, clone_b))


def test_classifier_rejects_reused_runtime_identity() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    clone_b = make_event(
        event_id=clone_b.event_id,
        sequence_number=clone_b.sequence_number,
        event_type=clone_b.event_type,
        runtime_id=clone_a.runtime_id,
        execution_id=clone_b.execution_id,
        state_id=clone_b.state_id,
        host_id=clone_b.host_id,
        address=clone_b.address,
        parent_event_ids=clone_b.parent_event_ids,
        parent_state_ids=clone_b.parent_state_ids,
        evidence_ids=clone_b.evidence_ids,
        snapshot_id=clone_b.snapshot_id,
        branch_id=clone_b.branch_id,
    )

    with pytest.raises(CloneClassificationError, match="(?i)runtime"):
        CloneClassifier().classify(parent, (clone_a, clone_b))


def test_classifier_rejects_reused_execution_identity() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    clone_b = make_event(
        event_id=clone_b.event_id,
        sequence_number=clone_b.sequence_number,
        event_type=clone_b.event_type,
        runtime_id=clone_b.runtime_id,
        execution_id=clone_a.execution_id,
        state_id=clone_b.state_id,
        host_id=clone_b.host_id,
        address=clone_b.address,
        parent_event_ids=clone_b.parent_event_ids,
        parent_state_ids=clone_b.parent_state_ids,
        evidence_ids=clone_b.evidence_ids,
        snapshot_id=clone_b.snapshot_id,
        branch_id=clone_b.branch_id,
    )

    with pytest.raises(CloneClassificationError, match="(?i)execution"):
        CloneClassifier().classify(parent, (clone_a, clone_b))


def test_classifier_rejects_missing_parent_link() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    clone_b = make_event(
        event_id=clone_b.event_id,
        sequence_number=clone_b.sequence_number,
        event_type=clone_b.event_type,
        runtime_id=clone_b.runtime_id,
        execution_id=clone_b.execution_id,
        state_id=clone_b.state_id,
        host_id=clone_b.host_id,
        address=clone_b.address,
        parent_state_ids=clone_b.parent_state_ids,
        evidence_ids=clone_b.evidence_ids,
        snapshot_id=clone_b.snapshot_id,
        branch_id=clone_b.branch_id,
    )

    with pytest.raises(CloneClassificationError, match="(?i)parent"):
        CloneClassifier().classify(parent, (clone_a, clone_b))


def test_classifier_rejects_different_snapshot_identity() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    clone_b = make_event(
        event_id=clone_b.event_id,
        sequence_number=clone_b.sequence_number,
        event_type=clone_b.event_type,
        runtime_id=clone_b.runtime_id,
        execution_id=clone_b.execution_id,
        state_id=clone_b.state_id,
        host_id=clone_b.host_id,
        address=clone_b.address,
        parent_event_ids=clone_b.parent_event_ids,
        parent_state_ids=clone_b.parent_state_ids,
        evidence_ids=clone_b.evidence_ids,
        snapshot_id="SNAPSHOT-999",
        branch_id=clone_b.branch_id,
    )

    with pytest.raises(CloneClassificationError, match="(?i)snapshot"):
        CloneClassifier().classify(parent, (clone_a, clone_b))


def test_classifier_requires_tuple_children() -> None:
    parent, clone_a, clone_b = make_valid_clone_set()

    with pytest.raises(TypeError, match="tuple"):
        CloneClassifier().classify(
            parent,
            [clone_a, clone_b],  # type: ignore[arg-type]
        )


def test_classifier_requires_process_event_parent() -> None:
    _, clone_a, clone_b = make_valid_clone_set()

    with pytest.raises(TypeError, match="ProcessEvent"):
        CloneClassifier().classify(
            "EV-001",  # type: ignore[arg-type]
            (clone_a, clone_b),
        )