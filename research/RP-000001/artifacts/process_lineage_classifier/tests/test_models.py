from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

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
from models import (
    BindingAssessment,
    ContinuityClassification,
    ProcessEvent,
    ProcessState,
    TransitionEvidence,
)


def make_event() -> ProcessEvent:
    return ProcessEvent(
        event_id="EV-001",
        event_type=EventType.START,
        timestamp=datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc),
        sequence_number=1,
        service_id="SERVICE-A",
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
        host_id="HOST-001",
        address="10.0.0.10",
        authority_role="PRIMARY",
    )


def test_process_event_is_created() -> None:
    event = make_event()

    assert event.event_id == "EV-001"
    assert event.event_type is EventType.START
    assert event.sequence_number == 1
    assert event.parent_event_ids == ()


def test_process_event_is_immutable() -> None:
    event = make_event()

    with pytest.raises(FrozenInstanceError):
        event.event_id = "EV-002"  # type: ignore[misc]


def test_process_event_rejects_empty_required_field() -> None:
    with pytest.raises(ValueError, match="event_id"):
        ProcessEvent(
            event_id="",
            event_type=EventType.START,
            timestamp=datetime.now(timezone.utc),
            sequence_number=1,
            service_id="SERVICE-A",
            runtime_id="RUNTIME-001",
            execution_id="EXEC-001",
            state_id="STATE-001",
            host_id="HOST-001",
            address="10.0.0.10",
            authority_role="PRIMARY",
        )


def test_process_event_rejects_negative_sequence() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ProcessEvent(
            event_id="EV-001",
            event_type=EventType.START,
            timestamp=datetime.now(timezone.utc),
            sequence_number=-1,
            service_id="SERVICE-A",
            runtime_id="RUNTIME-001",
            execution_id="EXEC-001",
            state_id="STATE-001",
            host_id="HOST-001",
            address="10.0.0.10",
            authority_role="PRIMARY",
        )


def test_process_event_requires_tuple_parent_ids() -> None:
    with pytest.raises(TypeError, match="parent_event_ids"):
        ProcessEvent(
            event_id="EV-001",
            event_type=EventType.START,
            timestamp=datetime.now(timezone.utc),
            sequence_number=1,
            service_id="SERVICE-A",
            runtime_id="RUNTIME-001",
            execution_id="EXEC-001",
            state_id="STATE-001",
            host_id="HOST-001",
            address="10.0.0.10",
            authority_role="PRIMARY",
            parent_event_ids=["EV-000"],  # type: ignore[arg-type]
        )


def test_process_state_is_created_and_immutable() -> None:
    state = ProcessState(
        service_id="SERVICE-A",
        runtime_id="RUNTIME-001",
        execution_id="EXEC-001",
        state_id="STATE-001",
        host_id="HOST-001",
        address="10.0.0.10",
        authority_role="PRIMARY",
        is_active=True,
        state_hash="abc123",
    )

    assert state.is_active is True
    assert state.state_hash == "abc123"

    with pytest.raises(FrozenInstanceError):
        state.is_active = False  # type: ignore[misc]


def test_process_state_rejects_non_boolean_active_status() -> None:
    with pytest.raises(TypeError, match="is_active"):
        ProcessState(
            service_id="SERVICE-A",
            runtime_id="RUNTIME-001",
            execution_id="EXEC-001",
            state_id="STATE-001",
            host_id="HOST-001",
            address="10.0.0.10",
            authority_role="PRIMARY",
            is_active="yes",  # type: ignore[arg-type]
        )


def test_transition_evidence_is_created() -> None:
    evidence = TransitionEvidence(
        evidence_id="EVD-001",
        evidence_type="PARENT_LINK",
        source_event_id="EV-001",
        target_event_id="EV-002",
        is_verified=True,
    )

    assert evidence.is_verified is True
    assert evidence.evidence_type == "PARENT_LINK"


def test_transition_evidence_rejects_non_boolean_verification() -> None:
    with pytest.raises(TypeError, match="is_verified"):
        TransitionEvidence(
            evidence_id="EVD-001",
            evidence_type="PARENT_LINK",
            source_event_id="EV-001",
            target_event_id="EV-002",
            is_verified=1,  # type: ignore[arg-type]
        )


def test_binding_assessment_is_created() -> None:
    assessment = BindingAssessment(
        binding_status=BindingStatus.BOUND,
        reference_type="SERVICE_ID",
        reference_value="SERVICE-A",
        target_type="RUNTIME",
        target_value="RUNTIME-001",
        reasons=("Reference resolves to declared runtime.",),
    )

    assert assessment.binding_status is BindingStatus.BOUND
    assert assessment.missing_evidence == ()


def test_binding_assessment_rejects_wrong_enum_type() -> None:
    with pytest.raises(TypeError, match="binding_status"):
        BindingAssessment(
            binding_status="BOUND",  # type: ignore[arg-type]
            reference_type="SERVICE_ID",
            reference_value="SERVICE-A",
            target_type="RUNTIME",
            target_value="RUNTIME-001",
        )


def test_continuity_classification_is_created() -> None:
    result = ContinuityClassification(
        transition_id="TR-001",
        event_type=EventType.ADDRESS_CHANGE,
        service_continuity=ContinuityStatus.CONTINUOUS,
        runtime_continuity=ContinuityStatus.CONTINUOUS,
        execution_continuity=ContinuityStatus.CONTINUOUS,
        state_continuity=ContinuityStatus.CONTINUOUS,
        authority_continuity=ContinuityStatus.CONTINUOUS,
        availability_continuity=ContinuityStatus.CONTINUOUS,
        state_lineage=LineageStatus.LINEAR,
        binding_status=BindingStatus.REBOUND,
        conflict_status=ConflictStatus.CLEAR,
        transition_status=TransitionStatus.ADDRESS_REBOUND,
        operational_status=OperationalStatus.PASS,
        confidence=ConfidenceLevel.HIGH,
        applied_rules=("ADDRESS_CHANGE",),
        reasons=("Only the address changed.",),
    )

    assert result.classifier_version == "0.1.0"
    assert result.operational_status is OperationalStatus.PASS
    assert result.binding_status is BindingStatus.REBOUND


def test_continuity_classification_rejects_non_tuple_reasons() -> None:
    with pytest.raises(TypeError, match="reasons"):
        ContinuityClassification(
            transition_id="TR-001",
            event_type=EventType.ADDRESS_CHANGE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.ADDRESS_REBOUND,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            reasons=["Only the address changed."],  # type: ignore[arg-type]
        )