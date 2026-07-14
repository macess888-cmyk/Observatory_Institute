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
from services.authority_convergence_classifier import (
    AuthorityConvergenceClassificationError,
    AuthorityConvergenceClassifier,
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
    evidence_ids: tuple[str, ...] = (),
    service_id: str = "SERVICE-A",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=EventType.AUTHORITY_CONVERGENCE,
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
        evidence_ids=evidence_ids,
    )


def make_valid_convergence_set() -> tuple[ProcessEvent, ...]:
    former_primary = make_event(
        event_id="EV-001",
        sequence_number=1,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
        host_id="HOST-A",
        address="10.0.0.10",
        authority_role="SECONDARY",
        evidence_ids=(
            "EVD-AUTHORITY-REVOCATION-001",
            "EVD-CONVERGENCE-ACK-001",
        ),
    )
    elected_primary = make_event(
        event_id="EV-002",
        sequence_number=2,
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
        host_id="HOST-B",
        address="10.0.0.20",
        authority_role="PRIMARY",
        evidence_ids=(
            "EVD-AUTHORITY-GRANT-001",
            "EVD-QUORUM-CONFIRMATION-001",
            "EVD-CONVERGENCE-ACK-002",
        ),
    )
    observer = make_event(
        event_id="EV-003",
        sequence_number=3,
        runtime_id="RUNTIME-C",
        execution_id="EXEC-C",
        state_id="STATE-B",
        host_id="HOST-C",
        address="10.0.0.30",
        authority_role="SECONDARY",
        evidence_ids=(
            "EVD-CONVERGENCE-ACK-003",
        ),
    )
    return former_primary, elected_primary, observer


def test_classifier_accepts_verified_authority_convergence() -> None:
    events = make_valid_convergence_set()

    result = AuthorityConvergenceClassifier().classify(events)

    assert result.event_type is EventType.AUTHORITY_CONVERGENCE
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.RECONCILED
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.AUTHORITY_CONVERGED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "ACV-001" in result.applied_rules


def test_classifier_explains_verified_convergence() -> None:
    events = make_valid_convergence_set()

    result = AuthorityConvergenceClassifier().classify(events)

    assert any("single primary" in reason.lower() for reason in result.reasons)
    assert any("quorum" in reason.lower() for reason in result.reasons)
    assert any("revocation" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_incomplete_convergence_evidence() -> None:
    former_primary, elected_primary, observer = make_valid_convergence_set()

    unverified_primary = make_event(
        event_id=elected_primary.event_id,
        sequence_number=elected_primary.sequence_number,
        runtime_id=elected_primary.runtime_id,
        execution_id=elected_primary.execution_id,
        state_id=elected_primary.state_id,
        host_id=elected_primary.host_id,
        address=elected_primary.address,
        authority_role=elected_primary.authority_role,
        evidence_ids=(),
    )

    result = AuthorityConvergenceClassifier().classify(
        (former_primary, unverified_primary, observer)
    )

    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "ACV-002" in result.applied_rules


def test_classifier_returns_hold_when_multiple_primaries_remain() -> None:
    former_primary, elected_primary, observer = make_valid_convergence_set()

    conflicting = make_event(
        event_id=former_primary.event_id,
        sequence_number=former_primary.sequence_number,
        runtime_id=former_primary.runtime_id,
        execution_id=former_primary.execution_id,
        state_id=former_primary.state_id,
        host_id=former_primary.host_id,
        address=former_primary.address,
        authority_role="PRIMARY",
        evidence_ids=former_primary.evidence_ids,
    )

    result = AuthorityConvergenceClassifier().classify(
        (conflicting, elected_primary, observer)
    )

    assert result.authority_continuity is ContinuityStatus.CONFLICTED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "ACV-003" in result.applied_rules


def test_classifier_returns_hold_for_state_divergence() -> None:
    former_primary, elected_primary, observer = make_valid_convergence_set()

    divergent_observer = make_event(
        event_id=observer.event_id,
        sequence_number=observer.sequence_number,
        runtime_id=observer.runtime_id,
        execution_id=observer.execution_id,
        state_id="STATE-C",
        host_id=observer.host_id,
        address=observer.address,
        authority_role=observer.authority_role,
        evidence_ids=observer.evidence_ids
        + ("EVD-STATE-DIVERGENCE-001",),
    )

    result = AuthorityConvergenceClassifier().classify(
        (former_primary, elected_primary, divergent_observer)
    )

    assert result.state_continuity is ContinuityStatus.CONFLICTED
    assert result.state_lineage is LineageStatus.CONFLICTED
    assert result.conflict_status is ConflictStatus.CONFLICTED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "ACV-004" in result.applied_rules


def test_classifier_rejects_single_event() -> None:
    event = make_valid_convergence_set()[0]

    with pytest.raises(
        AuthorityConvergenceClassificationError,
        match="at least two",
    ):
        AuthorityConvergenceClassifier().classify((event,))


def test_classifier_rejects_non_tuple_input() -> None:
    events = make_valid_convergence_set()

    with pytest.raises(TypeError, match="tuple"):
        AuthorityConvergenceClassifier().classify(
            list(events)  # type: ignore[arg-type]
        )


def test_classifier_rejects_non_process_event_member() -> None:
    first, second, _ = make_valid_convergence_set()

    with pytest.raises(TypeError, match="ProcessEvent"):
        AuthorityConvergenceClassifier().classify(
            (first, second, "EV-003")  # type: ignore[arg-type]
        )


def test_classifier_rejects_mixed_service_identities() -> None:
    first, second, third = make_valid_convergence_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        evidence_ids=third.evidence_ids,
        service_id="SERVICE-B",
    )

    with pytest.raises(
        AuthorityConvergenceClassificationError,
        match="service",
    ):
        AuthorityConvergenceClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_duplicate_event_identity() -> None:
    first, second, third = make_valid_convergence_set()

    invalid = make_event(
        event_id=first.event_id,
        sequence_number=third.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        AuthorityConvergenceClassificationError,
        match="event identity",
    ):
        AuthorityConvergenceClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_duplicate_runtime_identity() -> None:
    first, second, third = make_valid_convergence_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        runtime_id=first.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        AuthorityConvergenceClassificationError,
        match="runtime identity",
    ):
        AuthorityConvergenceClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_duplicate_execution_identity() -> None:
    first, second, third = make_valid_convergence_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=third.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=first.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        AuthorityConvergenceClassificationError,
        match="execution identity",
    ):
        AuthorityConvergenceClassifier().classify(
            (first, second, invalid)
        )


def test_classifier_rejects_non_increasing_sequences() -> None:
    first, second, third = make_valid_convergence_set()

    invalid = make_event(
        event_id=third.event_id,
        sequence_number=second.sequence_number,
        runtime_id=third.runtime_id,
        execution_id=third.execution_id,
        state_id=third.state_id,
        host_id=third.host_id,
        address=third.address,
        authority_role=third.authority_role,
        evidence_ids=third.evidence_ids,
    )

    with pytest.raises(
        AuthorityConvergenceClassificationError,
        match="sequence",
    ):
        AuthorityConvergenceClassifier().classify(
            (first, second, invalid)
        )