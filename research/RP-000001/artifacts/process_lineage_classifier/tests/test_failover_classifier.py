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
from services.failover_classifier import (
    FailoverClassificationError,
    FailoverClassifier,
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
    is_active_address: str,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    service_id: str = "SERVICE-A",
    host_id: str = "HOST-001",
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
        address=is_active_address,
        authority_role=authority_role,
        parent_event_ids=parent_event_ids,
        parent_state_ids=parent_state_ids,
        evidence_ids=evidence_ids,
    )


def make_valid_failover() -> tuple[ProcessEvent, ProcessEvent]:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-PRIMARY",
        execution_id="EXEC-PRIMARY",
        state_id="STATE-100",
        authority_role="PRIMARY",
        is_active_address="10.0.0.10",
        host_id="HOST-PRIMARY",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.FAILOVER,
        runtime_id="RUNTIME-SECONDARY",
        execution_id="EXEC-SECONDARY",
        state_id="STATE-100",
        authority_role="PRIMARY",
        is_active_address="10.0.0.20",
        host_id="HOST-SECONDARY",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-FAILOVER-001",
            "EVD-AUTHORITY-TRANSFER-001",
            "EVD-STATE-SYNC-001",
            "EVD-SOURCE-DEACTIVATION-001",
        ),
    )
    return previous, current


def test_classifier_accepts_valid_failover() -> None:
    previous, current = make_valid_failover()

    result = FailoverClassifier().classify(previous, current)

    assert result.event_type is EventType.FAILOVER
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.TERMINATED
    assert result.execution_continuity is ContinuityStatus.TERMINATED
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.FAILOVER
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "FO-001" in result.applied_rules


def test_classifier_explains_valid_failover() -> None:
    previous, current = make_valid_failover()

    result = FailoverClassifier().classify(previous, current)

    assert any("authority" in reason.lower() for reason in result.reasons)
    assert any("runtime" in reason.lower() for reason in result.reasons)
    assert any("state" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_degraded_for_stale_failover() -> None:
    previous, current = make_valid_failover()

    stale = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id="STATE-099",
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=("STATE-099",),
        evidence_ids=(
            "EVD-FAILOVER-001",
            "EVD-AUTHORITY-TRANSFER-001",
            "EVD-STALE-STATE-001",
            "EVD-SOURCE-DEACTIVATION-001",
        ),
    )

    result = FailoverClassifier().classify(previous, stale)

    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.DEGRADED
    assert result.state_lineage is LineageStatus.DISCONTINUOUS
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.MODERATE
    assert "FO-002" in result.applied_rules


def test_classifier_returns_hold_for_missing_failover_evidence() -> None:
    previous, current = make_valid_failover()

    unverified = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(),
    )

    result = FailoverClassifier().classify(previous, unverified)

    assert result.runtime_continuity is ContinuityStatus.UNVERIFIED
    assert result.execution_continuity is ContinuityStatus.UNKNOWN
    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.missing_evidence
    assert "FO-003" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_failover()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.RESTART,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(FailoverClassificationError, match="FAILOVER"):
        FailoverClassifier().classify(previous, invalid)


def test_classifier_rejects_unchanged_runtime_identity() -> None:
    previous, current = make_valid_failover()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=previous.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(FailoverClassificationError, match="(?i)runtime"):
        FailoverClassifier().classify(previous, invalid)


def test_classifier_rejects_unchanged_execution_identity() -> None:
    previous, current = make_valid_failover()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=previous.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(FailoverClassificationError, match="(?i)execution"):
        FailoverClassifier().classify(previous, invalid)


def test_classifier_rejects_changed_service_identity() -> None:
    previous, current = make_valid_failover()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        service_id="SERVICE-B",
    )

    with pytest.raises(FailoverClassificationError, match="(?i)service"):
        FailoverClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_failover()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        is_active_address=current.address,
        host_id=current.host_id,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(FailoverClassificationError, match="(?i)parent"):
        FailoverClassifier().classify(previous, invalid)


def test_classifier_rejects_non_primary_successor() -> None:
    previous, current = make_valid_failover()

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role="SECONDARY",
        is_active_address=current.address,
        host_id=current.host_id,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(FailoverClassificationError, match="(?i)PRIMARY"):
        FailoverClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_failover()

    with pytest.raises(TypeError, match="ProcessEvent"):
        FailoverClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )