from datetime import datetime, timedelta, timezone

import pytest

from enums import EventType
from models import ProcessEvent
from services.transition_validator import (
    DuplicateEventError,
    InvalidEventError,
    MissingParentError,
    TransitionValidator,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: EventType = EventType.START,
    parent_event_ids: tuple[str, ...] = (),
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=event_type,
        timestamp=datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
        + timedelta(seconds=sequence_number),
        sequence_number=sequence_number,
        service_id="SERVICE-A",
        runtime_id=f"RUNTIME-{sequence_number:03d}",
        execution_id=f"EXEC-{sequence_number:03d}",
        state_id=f"STATE-{sequence_number:03d}",
        host_id="HOST-001",
        address="10.0.0.10",
        authority_role="PRIMARY",
        parent_event_ids=parent_event_ids,
    )


def test_validator_accepts_valid_start_event() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
    )

    validator = TransitionValidator()

    result = validator.validate((event,))

    assert result is True


def test_validator_accepts_valid_parent_child_sequence() -> None:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
    )
    child = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TransitionValidator()

    result = validator.validate((parent, child))

    assert result is True


def test_validator_rejects_duplicate_event_ids() -> None:
    first = make_event(
        event_id="EV-001",
        sequence_number=1,
    )
    duplicate = make_event(
        event_id="EV-001",
        sequence_number=2,
    )

    validator = TransitionValidator()

    with pytest.raises(DuplicateEventError, match="EV-001"):
        validator.validate((first, duplicate))


def test_validator_rejects_missing_parent() -> None:
    child = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TransitionValidator()

    with pytest.raises(MissingParentError, match="EV-001"):
        validator.validate((child,))


def test_validator_rejects_child_sequence_not_after_parent() -> None:
    parent = make_event(
        event_id="EV-001",
        sequence_number=2,
    )
    child = make_event(
        event_id="EV-002",
        sequence_number=1,
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TransitionValidator()

    with pytest.raises(InvalidEventError, match="sequence"):
        validator.validate((parent, child))


def test_validator_rejects_self_parent_reference() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        parent_event_ids=("EV-001",),
    )

    validator = TransitionValidator()

    with pytest.raises(InvalidEventError, match="own parent"):
        validator.validate((event,))


def test_validator_rejects_empty_event_collection() -> None:
    validator = TransitionValidator()

    with pytest.raises(InvalidEventError, match="at least one"):
        validator.validate(())


def test_validator_requires_tuple_input() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
    )

    validator = TransitionValidator()

    with pytest.raises(TypeError, match="tuple"):
        validator.validate([event])  # type: ignore[arg-type]


def test_validator_rejects_non_process_event_member() -> None:
    validator = TransitionValidator()

    with pytest.raises(TypeError, match="ProcessEvent"):
        validator.validate(("EV-001",))  # type: ignore[arg-type]