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
from services.split_brain_classifier import (
    SplitBrainClassificationError,
    SplitBrainClassifier,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    runtime_id: str,
    execution_id: str,
    state_id: str,
    host_id: str,
    address: str,
    authority_role: str = "PRIMARY",
    event_type: EventType = EventType.START,
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


def make_split_brain_pair() -> tuple[ProcessEvent, ProcessEvent]:
    first = make_event(
        event_id="EV-001",
        sequence_number=1,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
        host_id="HOST-A",
        address="10.0.0.10",
        evidence_ids=(
            "EVD-ACTIVE-PRIMARY-001",
            "EVD-LEASE-VALID-001",
        ),
    )
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        host_id="HOST-B",
        address="10.0.0.20",
        evidence_ids=(
            "EVD-ACTIVE-PRIMARY-002",
            "EVD-LEASE-VALID-002",
        ),
    )
    return first, second


def test_classifier_detects_confirmed_split_brain() -> None:
    first, second = make_split_brain_pair()
    result = SplitBrainClassifier().classify((first, second))

    assert result.event_type is EventType.SPLIT_BRAIN
    assert result.service_continuity is ContinuityStatus.UNVERIFIED
    assert result.runtime_continuity is ContinuityStatus.CONFLICTED
    assert result.execution_continuity is ContinuityStatus.CONFLICTED
    assert result.state_continuity is ContinuityStatus.CONFLICTED
    assert result.authority_continuity is ContinuityStatus.CONFLICTED
    assert result.availability_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.state_lineage is LineageStatus.CONFLICTED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.transition_status is TransitionStatus.SPLIT_BRAIN_DETECTED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.HIGH
    assert "SB-001" in result.applied_rules
    assert result.conflicts


def test_classifier_explains_confirmed_split_brain() -> None:
    first, second = make_split_brain_pair()
    result = SplitBrainClassifier().classify((first, second))

    assert any("primary" in reason.lower() for reason in result.reasons)
    assert any("authority" in reason.lower() for reason in result.reasons)
    assert any("state" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts


def test_classifier_returns_hold_for_unverified_split_brain() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        evidence_ids=(),
    )

    result = SplitBrainClassifier().classify((first, second))

    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "SB-002" in result.applied_rules


def test_classifier_returns_clear_when_only_one_primary_exists() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        authority_role="SECONDARY",
        evidence_ids=(
            "EVD-SECONDARY-ROLE-001",
            "EVD-LEASE-VALID-002",
        ),
    )

    result = SplitBrainClassifier().classify((first, second))

    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.operational_status is OperationalStatus.PASS
    assert result.conflicts == ()
    assert "SB-003" in result.applied_rules


def test_classifier_rejects_single_event() -> None:
    first, _ = make_split_brain_pair()

    with pytest.raises(SplitBrainClassificationError, match="at least two"):
        SplitBrainClassifier().classify((first,))


def test_classifier_rejects_mixed_service_identities() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        service_id="SERVICE-B",
        evidence_ids=second.evidence_ids,
    )

    with pytest.raises(SplitBrainClassificationError, match="service"):
        SplitBrainClassifier().classify((first, second))


def test_classifier_rejects_duplicate_runtime_identity() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        runtime_id=first.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        evidence_ids=second.evidence_ids,
    )

    with pytest.raises(SplitBrainClassificationError, match="runtime"):
        SplitBrainClassifier().classify((first, second))


def test_classifier_rejects_duplicate_execution_identity() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        runtime_id=second.runtime_id,
        execution_id=first.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        evidence_ids=second.evidence_ids,
    )

    with pytest.raises(SplitBrainClassificationError, match="execution"):
        SplitBrainClassifier().classify((first, second))


def test_classifier_rejects_duplicate_event_identity() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=first.event_id,
        sequence_number=second.sequence_number,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        evidence_ids=second.evidence_ids,
    )

    with pytest.raises(SplitBrainClassificationError, match="event"):
        SplitBrainClassifier().classify((first, second))


def test_classifier_rejects_non_tuple_input() -> None:
    first, second = make_split_brain_pair()

    with pytest.raises(TypeError, match="tuple"):
        SplitBrainClassifier().classify(
            [first, second]  # type: ignore[arg-type]
        )


def test_classifier_rejects_non_process_event_member() -> None:
    first, _ = make_split_brain_pair()

    with pytest.raises(TypeError, match="ProcessEvent"):
        SplitBrainClassifier().classify(
            (first, "EV-002")  # type: ignore[arg-type]
        )


def test_classifier_rejects_non_increasing_sequences() -> None:
    first, second = make_split_brain_pair()
    second = make_event(
        event_id=second.event_id,
        sequence_number=first.sequence_number,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        host_id=second.host_id,
        address=second.address,
        evidence_ids=second.evidence_ids,
    )

    with pytest.raises(SplitBrainClassificationError, match="sequence"):
        SplitBrainClassifier().classify((first, second))