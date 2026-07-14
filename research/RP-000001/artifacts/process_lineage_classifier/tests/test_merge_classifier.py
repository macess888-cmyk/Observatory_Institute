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
from services.merge_classifier import (
    MergeClassificationError,
    MergeClassifier,
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
    merge_id: str | None = None,
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
        merge_id=merge_id,
    )


def make_valid_merge_set() -> tuple[
    ProcessEvent,
    ProcessEvent,
    ProcessEvent,
]:
    parent_a = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
        host_id="HOST-A",
        address="10.0.0.20",
        authority_role="SECONDARY",
    )
    parent_b = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.START,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        host_id="HOST-B",
        address="10.0.0.30",
        authority_role="SECONDARY",
    )
    merged = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.MERGE,
        runtime_id="RUNTIME-M",
        execution_id="EXEC-M",
        state_id="STATE-M",
        host_id="HOST-M",
        address="10.0.0.40",
        parent_event_ids=("EV-001", "EV-002"),
        parent_state_ids=("STATE-A", "STATE-B"),
        evidence_ids=("EVD-MERGE-001", "EVD-STATE-RECONCILE-001"),
        merge_id="MERGE-001",
        authority_role="PRIMARY",
    )

    return parent_a, parent_b, merged


def test_classifier_accepts_valid_merge() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    result = MergeClassifier().classify((parent_a, parent_b), merged)

    assert result.event_type is EventType.MERGE
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
    assert result.state_lineage is LineageStatus.MERGED
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.MERGED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "MR-001" in result.applied_rules


def test_classifier_explains_valid_merge() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    result = MergeClassifier().classify((parent_a, parent_b), merged)

    assert any("multiple parent" in reason.lower() for reason in result.reasons)
    assert any("new state" in reason.lower() for reason in result.reasons)
    assert any("reconciliation" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_rejects_single_parent() -> None:
    parent_a, _, merged = make_valid_merge_set()

    with pytest.raises(MergeClassificationError, match="at least two"):
        MergeClassifier().classify((parent_a,), merged)


def test_classifier_rejects_wrong_current_event_type() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=EventType.BRANCH,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="MERGE"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_missing_parent_event_reference() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=("EV-001",),
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="parent event"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_missing_parent_state_reference() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=("STATE-A",),
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="parent state"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_reused_state_identity() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=parent_a.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="new state"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_reused_runtime_identity() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=parent_a.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="(?i)runtime"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_reused_execution_identity() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=parent_b.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="(?i)execution"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_changed_service_identity() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
        service_id="SERVICE-B",
    )

    with pytest.raises(MergeClassificationError, match="(?i)service"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_missing_merge_identity() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
    )

    with pytest.raises(MergeClassificationError, match="merge identity"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_missing_merge_evidence() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=merged.sequence_number,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="(?i)evidence"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_rejects_sequence_before_parent() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    current = make_event(
        event_id=merged.event_id,
        sequence_number=1,
        event_type=merged.event_type,
        runtime_id=merged.runtime_id,
        execution_id=merged.execution_id,
        state_id=merged.state_id,
        host_id=merged.host_id,
        address=merged.address,
        parent_event_ids=merged.parent_event_ids,
        parent_state_ids=merged.parent_state_ids,
        evidence_ids=merged.evidence_ids,
        merge_id=merged.merge_id,
    )

    with pytest.raises(MergeClassificationError, match="(?i)sequence"):
        MergeClassifier().classify((parent_a, parent_b), current)


def test_classifier_requires_tuple_parents() -> None:
    parent_a, parent_b, merged = make_valid_merge_set()

    with pytest.raises(TypeError, match="tuple"):
        MergeClassifier().classify(
            [parent_a, parent_b],  # type: ignore[arg-type]
            merged,
        )


def test_classifier_requires_process_event_current() -> None:
    parent_a, parent_b, _ = make_valid_merge_set()

    with pytest.raises(TypeError, match="ProcessEvent"):
        MergeClassifier().classify(
            (parent_a, parent_b),
            "EV-003",  # type: ignore[arg-type]
        )