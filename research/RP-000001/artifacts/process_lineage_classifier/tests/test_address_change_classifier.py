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
from services.address_change_classifier import (
    AddressChangeClassifier,
    AddressChangeClassificationError,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    address: str,
    parent_event_ids: tuple[str, ...] = (),
    event_type: EventType = EventType.ADDRESS_CHANGE,
    service_id: str = "SERVICE-A",
    runtime_id: str = "RUNTIME-001",
    execution_id: str = "EXEC-001",
    state_id: str = "STATE-001",
    host_id: str = "HOST-001",
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
    )


def test_classifier_accepts_valid_address_change() -> None:
    previous = make_event(
        event_id="EV-001", sequence_number=1,
        event_type=EventType.START, address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002", sequence_number=2,
        address="10.0.0.20", parent_event_ids=("EV-001",),
    )
    result = AddressChangeClassifier().classify(previous, current)
    assert result.event_type is EventType.ADDRESS_CHANGE
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.ADDRESS_REBOUND
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "AC-001" in result.applied_rules


def test_classifier_explains_address_change() -> None:
    previous = make_event(
        event_id="EV-001", sequence_number=1,
        event_type=EventType.START, address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002", sequence_number=2,
        address="10.0.0.20", parent_event_ids=("EV-001",),
    )
    result = AddressChangeClassifier().classify(previous, current)
    assert result.reasons
    assert any("address" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous = make_event(
        event_id="EV-001", sequence_number=1,
        event_type=EventType.START, address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002", sequence_number=2,
        event_type=EventType.RESTART, address="10.0.0.20",
        parent_event_ids=("EV-001",),
    )
    with pytest.raises(AddressChangeClassificationError, match="ADDRESS_CHANGE"):
        AddressChangeClassifier().classify(previous, current)


def test_classifier_rejects_unchanged_address() -> None:
    previous = make_event(
        event_id="EV-001", sequence_number=1,
        event_type=EventType.START, address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002", sequence_number=2,
        address="10.0.0.10", parent_event_ids=("EV-001",),
    )
    with pytest.raises(AddressChangeClassificationError, match="must change"):
        AddressChangeClassifier().classify(previous, current)


@pytest.mark.parametrize(
    ("field", "previous_value", "current_value"),
    [
        ("runtime", "RUNTIME-001", "RUNTIME-002"),
        ("execution", "EXEC-001", "EXEC-002"),
        ("service", "SERVICE-A", "SERVICE-B"),
    ],
)
def test_classifier_rejects_changed_identity(
    field: str, previous_value: str, current_value: str,
) -> None:
    previous = make_event(
        event_id="EV-001", sequence_number=1,
        event_type=EventType.START, address="10.0.0.10",
        **{f"{field}_id": previous_value},
    )
    current = make_event(
        event_id="EV-002", sequence_number=2,
        address="10.0.0.20", parent_event_ids=("EV-001",),
        **{f"{field}_id": current_value},
    )
    with pytest.raises(AddressChangeClassificationError, match=f"(?i){field}"):
        AddressChangeClassifier().classify(previous, current)


def test_classifier_rejects_missing_parent_link() -> None:
    previous = make_event(
        event_id="EV-001", sequence_number=1,
        event_type=EventType.START, address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002", sequence_number=2, address="10.0.0.20",
    )
    with pytest.raises(AddressChangeClassificationError, match="parent"):
        AddressChangeClassifier().classify(previous, current)


def test_classifier_requires_process_event_inputs() -> None:
    current = make_event(
        event_id="EV-002", sequence_number=2,
        address="10.0.0.20", parent_event_ids=("EV-001",),
    )
    with pytest.raises(TypeError, match="ProcessEvent"):
        AddressChangeClassifier().classify("EV-001", current)  # type: ignore[arg-type]