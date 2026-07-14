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
from services.demotion_classifier import (
    DemotionClassificationError,
    DemotionClassifier,
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
    )


def make_valid_demotion() -> tuple[ProcessEvent, ProcessEvent]:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="PRIMARY",
        host_id="HOST-A",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.DEMOTE,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="SECONDARY",
        host_id="HOST-A",
        address="10.0.0.10",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-DEMOTION-001",
            "EVD-AUTHORITY-REVOCATION-001",
            "EVD-SUCCESSOR-PRIMARY-001",
        ),
    )
    return previous, current


def test_classifier_accepts_valid_demotion() -> None:
    previous, current = make_valid_demotion()
    result = DemotionClassifier().classify(previous, current)

    assert result.event_type is EventType.DEMOTE
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.DEMOTED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "DM-001" in result.applied_rules


def test_classifier_explains_valid_demotion() -> None:
    previous, current = make_valid_demotion()
    result = DemotionClassifier().classify(previous, current)

    assert any("primary" in reason.lower() for reason in result.reasons)
    assert any("secondary" in reason.lower() for reason in result.reasons)
    assert any("revocation" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_missing_demotion_evidence() -> None:
    previous, current = make_valid_demotion()
    unverified = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(),
    )

    result = DemotionClassifier().classify(previous, unverified)

    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "DM-002" in result.applied_rules


def test_classifier_returns_hold_without_successor_primary() -> None:
    previous, current = make_valid_demotion()
    conflicted = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=(
            "EVD-DEMOTION-001",
            "EVD-AUTHORITY-REVOCATION-001",
            "EVD-NO-SUCCESSOR-PRIMARY-001",
        ),
    )

    result = DemotionClassifier().classify(previous, conflicted)

    assert result.authority_continuity is ContinuityStatus.INTERRUPTED
    assert result.availability_continuity is ContinuityStatus.DEGRADED
    assert result.binding_status is BindingStatus.EXPIRED
    assert result.conflict_status is ConflictStatus.CONFLICTED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "DM-003" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_demotion()
    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.PROMOTE,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(DemotionClassificationError, match="DEMOTE"):
        DemotionClassifier().classify(previous, invalid)


def test_classifier_rejects_non_primary_source() -> None:
    previous, current = make_valid_demotion()
    invalid_previous = make_event(
        event_id=previous.event_id,
        sequence_number=previous.sequence_number,
        event_type=previous.event_type,
        runtime_id=previous.runtime_id,
        execution_id=previous.execution_id,
        state_id=previous.state_id,
        authority_role="SECONDARY",
        host_id=previous.host_id,
        address=previous.address,
    )

    with pytest.raises(DemotionClassificationError, match="PRIMARY"):
        DemotionClassifier().classify(invalid_previous, current)


def test_classifier_rejects_non_secondary_target() -> None:
    previous, current = make_valid_demotion()
    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role="PRIMARY",
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(DemotionClassificationError, match="SECONDARY"):
        DemotionClassifier().classify(previous, invalid)


@pytest.mark.parametrize(
    ("field", "replacement", "pattern"),
    [
        ("runtime_id", "RUNTIME-B", "runtime"),
        ("execution_id", "EXEC-B", "execution"),
        ("state_id", "STATE-101", "state"),
        ("service_id", "SERVICE-B", "service"),
    ],
)
def test_classifier_rejects_changed_identity(
    field: str,
    replacement: str,
    pattern: str,
) -> None:
    previous, current = make_valid_demotion()
    values = {
        "runtime_id": current.runtime_id,
        "execution_id": current.execution_id,
        "state_id": current.state_id,
        "service_id": current.service_id,
    }
    values[field] = replacement

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=values["runtime_id"],
        execution_id=values["execution_id"],
        state_id=values["state_id"],
        authority_role=current.authority_role,
        host_id=current.host_id,
        address=current.address,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        service_id=values["service_id"],
    )

    with pytest.raises(DemotionClassificationError, match=f"(?i){pattern}"):
        DemotionClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_demotion()
    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        host_id=current.host_id,
        address=current.address,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(DemotionClassificationError, match="(?i)parent"):
        DemotionClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_demotion()

    with pytest.raises(TypeError, match="ProcessEvent"):
        DemotionClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )