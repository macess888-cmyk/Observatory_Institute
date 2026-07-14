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
from services.branch_classifier import (
    BranchClassificationError,
    BranchClassifier,
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
        branch_id=branch_id,
    )


def make_valid_branch_set() -> tuple[ProcessEvent, ProcessEvent, ProcessEvent]:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-PARENT",
        execution_id="EXEC-PARENT",
        state_id="STATE-001",
        authority_role="PRIMARY",
    )
    branch_a = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.BRANCH,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
        host_id="HOST-A",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        branch_id="BRANCH-A",
    )
    branch_b = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.BRANCH,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        host_id="HOST-B",
        address="10.0.0.30",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        branch_id="BRANCH-B",
    )
    return parent, branch_a, branch_b


def test_classifier_accepts_valid_branch() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    result = BranchClassifier().classify(parent, (branch_a, branch_b))

    assert result.event_type is EventType.BRANCH
    assert (
        result.service_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
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
    assert result.state_lineage is LineageStatus.BRANCHED
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.BRANCHED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "BR-001" in result.applied_rules


def test_classifier_explains_valid_branch() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    result = BranchClassifier().classify(parent, (branch_a, branch_b))

    assert any("distinct runtime" in reason.lower() for reason in result.reasons)
    assert any("shared parent" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_authority_collision() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_a = make_event(
        event_id=branch_a.event_id,
        sequence_number=branch_a.sequence_number,
        event_type=branch_a.event_type,
        runtime_id=branch_a.runtime_id,
        execution_id=branch_a.execution_id,
        state_id=branch_a.state_id,
        host_id=branch_a.host_id,
        address=branch_a.address,
        parent_event_ids=branch_a.parent_event_ids,
        parent_state_ids=branch_a.parent_state_ids,
        branch_id=branch_a.branch_id,
        authority_role="PRIMARY",
    )
    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_b.state_id,
        host_id=branch_b.host_id,
        address=branch_b.address,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_b.branch_id,
        authority_role="PRIMARY",
    )

    result = BranchClassifier().classify(parent, (branch_a, branch_b))

    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts


def test_classifier_rejects_single_branch_child() -> None:
    parent, branch_a, _ = make_valid_branch_set()

    with pytest.raises(BranchClassificationError, match="at least two"):
        BranchClassifier().classify(parent, (branch_a,))


def test_classifier_rejects_wrong_child_event_type() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=EventType.CLONE,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_b.state_id,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_b.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="BRANCH"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_rejects_reused_runtime_identity() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_a.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_b.state_id,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_b.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="(?i)runtime"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_rejects_reused_execution_identity() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_a.execution_id,
        state_id=branch_b.state_id,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_b.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="(?i)execution"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_rejects_reused_state_identity() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_a.state_id,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_b.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="(?i)state"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_rejects_missing_parent_link() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_b.state_id,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_b.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="(?i)parent"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_rejects_unrelated_parent_state() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_b.state_id,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=("STATE-999",),
        branch_id=branch_b.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="(?i)parent state"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_rejects_duplicate_branch_identity() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    branch_b = make_event(
        event_id=branch_b.event_id,
        sequence_number=branch_b.sequence_number,
        event_type=branch_b.event_type,
        runtime_id=branch_b.runtime_id,
        execution_id=branch_b.execution_id,
        state_id=branch_b.state_id,
        parent_event_ids=branch_b.parent_event_ids,
        parent_state_ids=branch_b.parent_state_ids,
        branch_id=branch_a.branch_id,
    )

    with pytest.raises(BranchClassificationError, match="(?i)branch"):
        BranchClassifier().classify(parent, (branch_a, branch_b))


def test_classifier_requires_tuple_children() -> None:
    parent, branch_a, branch_b = make_valid_branch_set()

    with pytest.raises(TypeError, match="tuple"):
        BranchClassifier().classify(
            parent,
            [branch_a, branch_b],  # type: ignore[arg-type]
        )


def test_classifier_requires_process_event_parent() -> None:
    _, branch_a, branch_b = make_valid_branch_set()

    with pytest.raises(TypeError, match="ProcessEvent"):
        BranchClassifier().classify(
            "EV-001",  # type: ignore[arg-type]
            (branch_a, branch_b),
        )