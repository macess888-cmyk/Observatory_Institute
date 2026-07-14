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
from services.resume_classifier import (
    ResumeClassificationError,
    ResumeClassifier,
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


def make_valid_resume() -> tuple[ProcessEvent, ProcessEvent]:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.PAUSE,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="NONE",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESUME,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        authority_role="PRIMARY",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-RESUME-001",
            "EVD-EXECUTION-RESUME-001",
            "EVD-STATE-VERIFY-001",
            "EVD-AUTHORITY-RESTORE-001",
            "EVD-NO-ACTIVE-PRIMARY-001",
        ),
    )
    return previous, current


def test_classifier_accepts_valid_resume() -> None:
    previous, current = make_valid_resume()
    result = ResumeClassifier().classify(previous, current)

    assert result.event_type is EventType.RESUME
    assert result.service_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.INTERRUPTED
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.RESUMED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "RSU-001" in result.applied_rules


def test_classifier_explains_valid_resume() -> None:
    previous, current = make_valid_resume()
    result = ResumeClassifier().classify(previous, current)

    assert any("paused" in reason.lower() for reason in result.reasons)
    assert any("execution" in reason.lower() for reason in result.reasons)
    assert any("authority" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_missing_resume_evidence() -> None:
    previous, current = make_valid_resume()
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
    )

    result = ResumeClassifier().classify(previous, unverified)

    assert result.execution_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "RSU-002" in result.applied_rules


def test_classifier_returns_hold_for_active_primary_conflict() -> None:
    previous, current = make_valid_resume()
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
            "EVD-RESUME-001",
            "EVD-EXECUTION-RESUME-001",
            "EVD-STATE-VERIFY-001",
            "EVD-AUTHORITY-RESTORE-001",
            "EVD-ACTIVE-PRIMARY-CONFLICT-001",
        ),
    )

    result = ResumeClassifier().classify(previous, conflicted)

    assert result.authority_continuity is ContinuityStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.COLLIDING
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "RSU-003" in result.applied_rules


def test_classifier_returns_hold_for_state_mismatch() -> None:
    previous, current = make_valid_resume()
    mismatched = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id="STATE-099",
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=("STATE-099",),
        evidence_ids=(
            "EVD-RESUME-001",
            "EVD-EXECUTION-RESUME-001",
            "EVD-STALE-STATE-001",
            "EVD-AUTHORITY-RESTORE-001",
            "EVD-NO-ACTIVE-PRIMARY-001",
        ),
    )

    result = ResumeClassifier().classify(previous, mismatched)

    assert result.state_continuity is ContinuityStatus.DEGRADED
    assert result.state_lineage is LineageStatus.DISCONTINUOUS
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.MODERATE
    assert "RSU-004" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous, current = make_valid_resume()
    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=EventType.REVIVE,
        runtime_id=current.runtime_id,
        execution_id=current.execution_id,
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
    )

    with pytest.raises(ResumeClassificationError, match="RESUME"):
        ResumeClassifier().classify(previous, invalid)


def test_classifier_rejects_non_paused_source() -> None:
    previous, current = make_valid_resume()
    invalid_previous = make_event(
        event_id=previous.event_id,
        sequence_number=previous.sequence_number,
        event_type=EventType.START,
        runtime_id=previous.runtime_id,
        execution_id=previous.execution_id,
        state_id=previous.state_id,
        authority_role="PRIMARY",
    )

    with pytest.raises(ResumeClassificationError, match="PAUSE"):
        ResumeClassifier().classify(invalid_previous, current)


@pytest.mark.parametrize(
    ("field", "replacement", "pattern"),
    [
        ("runtime_id", "RUNTIME-B", "runtime"),
        ("execution_id", "EXEC-B", "execution"),
        ("service_id", "SERVICE-B", "service"),
    ],
)
def test_classifier_rejects_changed_identity(
    field: str,
    replacement: str,
    pattern: str,
) -> None:
    previous, current = make_valid_resume()
    values = {
        "runtime_id": current.runtime_id,
        "execution_id": current.execution_id,
        "service_id": current.service_id,
    }
    values[field] = replacement

    invalid = make_event(
        event_id=current.event_id,
        sequence_number=current.sequence_number,
        event_type=current.event_type,
        runtime_id=values["runtime_id"],
        execution_id=values["execution_id"],
        state_id=current.state_id,
        authority_role=current.authority_role,
        parent_event_ids=current.parent_event_ids,
        parent_state_ids=current.parent_state_ids,
        evidence_ids=current.evidence_ids,
        service_id=values["service_id"],
    )

    with pytest.raises(ResumeClassificationError, match=f"(?i){pattern}"):
        ResumeClassifier().classify(previous, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    previous, current = make_valid_resume()
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
    )

    with pytest.raises(ResumeClassificationError, match="(?i)parent"):
        ResumeClassifier().classify(previous, invalid)


def test_classifier_rejects_non_primary_target() -> None:
    previous, current = make_valid_resume()
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
    )

    with pytest.raises(ResumeClassificationError, match="PRIMARY"):
        ResumeClassifier().classify(previous, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, current = make_valid_resume()

    with pytest.raises(TypeError, match="ProcessEvent"):
        ResumeClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )