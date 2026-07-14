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
from services.lineage_reconciliation_classifier import (
    LineageReconciliationClassificationError,
    LineageReconciliationClassifier,
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
    authority_role: str,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    service_id: str = "SERVICE-A",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=EventType.LINEAGE_RECONCILIATION,
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


def make_valid_reconciliation_set() -> tuple[ProcessEvent, ...]:
    parent_a = make_event(
        event_id="EV-001",
        sequence_number=1,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
        host_id="HOST-A",
        address="10.0.0.10",
        authority_role="SECONDARY",
        evidence_ids=(
            "EVD-LINEAGE-ACK-001",
            "EVD-PARENT-STATE-VERIFY-001",
        ),
    )
    parent_b = make_event(
        event_id="EV-002",
        sequence_number=2,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        host_id="HOST-B",
        address="10.0.0.20",
        authority_role="SECONDARY",
        evidence_ids=(
            "EVD-LINEAGE-ACK-002",
            "EVD-PARENT-STATE-VERIFY-002",
        ),
    )
    reconciled = make_event(
        event_id="EV-003",
        sequence_number=3,
        runtime_id="RUNTIME-C",
        execution_id="EXEC-C",
        state_id="STATE-R",
        host_id="HOST-C",
        address="10.0.0.30",
        authority_role="PRIMARY",
        parent_event_ids=("EV-001", "EV-002"),
        parent_state_ids=("STATE-A", "STATE-B"),
        evidence_ids=(
            "EVD-LINEAGE-RECONCILIATION-001",
            "EVD-STATE-MERGE-VERIFY-001",
            "EVD-CONFLICT-RESOLUTION-001",
            "EVD-QUORUM-CONFIRMATION-001",
            "EVD-LINEAGE-ACK-003",
        ),
    )
    return parent_a, parent_b, reconciled


def test_classifier_accepts_verified_lineage_reconciliation() -> None:
    events = make_valid_reconciliation_set()

    result = LineageReconciliationClassifier().classify(events)

    assert result.event_type is EventType.LINEAGE_RECONCILIATION
    assert result.service_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.RECONCILED
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.LINEAGE_RECONCILED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "LR-001" in result.applied_rules


def test_classifier_explains_verified_reconciliation() -> None:
    events = make_valid_reconciliation_set()

    result = LineageReconciliationClassifier().classify(events)

    assert any("parent state" in reason.lower() for reason in result.reasons)
    assert any("reconciled" in reason.lower() for reason in result.reasons)
    assert any("conflict" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_incomplete_evidence() -> None:
    parent_a, parent_b, reconciled = make_valid_reconciliation_set()

    unverified = make_event(
        event_id=reconciled.event_id,
        sequence_number=reconciled.sequence_number,
        runtime_id=reconciled.runtime_id,
        execution_id=reconciled.execution_id,
        state_id=reconciled.state_id,
        host_id=reconciled.host_id,
        address=reconciled.address,
        authority_role=reconciled.authority_role,
        parent_event_ids=reconciled.parent_event_ids,
        parent_state_ids=reconciled.parent_state_ids,
        evidence_ids=(),
    )

    result = LineageReconciliationClassifier().classify(
        (parent_a, parent_b, unverified)
    )

    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_lineage is LineageStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "LR-002" in result.applied_rules


def test_classifier_returns_hold_for_unresolved_lineage_conflict() -> None:
    parent_a, parent_b, reconciled = make_valid_reconciliation_set()

    conflicted = make_event(
        event_id=reconciled.event_id,
        sequence_number=reconciled.sequence_number,
        runtime_id=reconciled.runtime_id,
        execution_id=reconciled.execution_id,
        state_id=reconciled.state_id,
        host_id=reconciled.host_id,
        address=reconciled.address,
        authority_role=reconciled.authority_role,
        parent_event_ids=reconciled.parent_event_ids,
        parent_state_ids=reconciled.parent_state_ids,
        evidence_ids=(
            "EVD-LINEAGE-RECONCILIATION-001",
            "EVD-STATE-MERGE-VERIFY-001",
            "EVD-UNRESOLVED-CONFLICT-001",
            "EVD-QUORUM-CONFIRMATION-001",
            "EVD-LINEAGE-ACK-003",
        ),
    )

    result = LineageReconciliationClassifier().classify(
        (parent_a, parent_b, conflicted)
    )

    assert result.state_continuity is ContinuityStatus.CONFLICTED
    assert result.state_lineage is LineageStatus.CONFLICTED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.CONFLICTED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "LR-003" in result.applied_rules


def test_classifier_returns_hold_for_missing_parent_state() -> None:
    parent_a, parent_b, reconciled = make_valid_reconciliation_set()

    incomplete = make_event(
        event_id=reconciled.event_id,
        sequence_number=reconciled.sequence_number,
        runtime_id=reconciled.runtime_id,
        execution_id=reconciled.execution_id,
        state_id=reconciled.state_id,
        host_id=reconciled.host_id,
        address=reconciled.address,
        authority_role=reconciled.authority_role,
        parent_event_ids=reconciled.parent_event_ids,
        parent_state_ids=("STATE-A",),
        evidence_ids=reconciled.evidence_ids,
    )

    result = LineageReconciliationClassifier().classify(
        (parent_a, parent_b, incomplete)
    )

    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_lineage is LineageStatus.UNVERIFIED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.missing_evidence
    assert "LR-004" in result.applied_rules


def test_classifier_rejects_single_event() -> None:
    event = make_valid_reconciliation_set()[0]

    with pytest.raises(
        LineageReconciliationClassificationError,
        match="at least three",
    ):
        LineageReconciliationClassifier().classify((event,))


def test_classifier_rejects_non_tuple_input() -> None:
    events = make_valid_reconciliation_set()

    with pytest.raises(TypeError, match="tuple"):
        LineageReconciliationClassifier().classify(
            list(events)  # type: ignore[arg-type]
        )


def test_classifier_rejects_non_process_event_member() -> None:
    first, second, _ = make_valid_reconciliation_set()

    with pytest.raises(TypeError, match="ProcessEvent"):
        LineageReconciliationClassifier().classify(
            (first, second, "EV-003")  # type: ignore[arg-type]
        )


def test_classifier_rejects_mixed_service_identities() -> None:
    first, second, third = make_valid_reconciliation_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        parent_event_ids=third.parent_event_ids,
        parent_state_ids=third.parent_state_ids,
        evidence_ids=third.evidence_ids,
        service_id="SERVICE-B",
    )

    with pytest.raises(
        LineageReconciliationClassificationError,
        match="service",
    ):
        LineageReconciliationClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_duplicate_event_identity() -> None:
    first, second, third = make_valid_reconciliation_set()

    invalid = make_event(
        event_id=first.event_id,
        sequence_number=third.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        parent_event_ids=third.parent_event_ids,
        parent_state_ids=third.parent_state_ids,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        LineageReconciliationClassificationError,
        match="event identity",
    ):
        LineageReconciliationClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_duplicate_runtime_identity() -> None:
    first, second, third = make_valid_reconciliation_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        runtime_id=first.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        parent_event_ids=third.parent_event_ids,
        parent_state_ids=third.parent_state_ids,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        LineageReconciliationClassificationError,
        match="runtime identity",
    ):
        LineageReconciliationClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_duplicate_execution_identity() -> None:
    first, second, third = make_valid_reconciliation_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=first.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        parent_event_ids=third.parent_event_ids,
        parent_state_ids=third.parent_state_ids,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        LineageReconciliationClassificationError,
        match="execution identity",
    ):
        LineageReconciliationClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_non_increasing_sequences() -> None:
    first, second, third = make_valid_reconciliation_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=second.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        parent_event_ids=third.parent_event_ids,
        parent_state_ids=third.parent_state_ids,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        LineageReconciliationClassificationError,
        match="sequence",
    ):
        LineageReconciliationClassifier().classify(
            (first, second, invalid)
        )