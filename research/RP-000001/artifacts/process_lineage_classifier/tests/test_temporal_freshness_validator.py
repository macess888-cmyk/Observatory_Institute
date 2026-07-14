from datetime import datetime, timedelta, timezone

import pytest

from enums import EventType
from models import ProcessEvent
from services.temporal_freshness_validator import (
    FutureTimestampError,
    StaleEventError,
    TemporalFreshnessValidator,
    TemporalOrderError,
)


REFERENCE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    timestamp: datetime,
    event_type: EventType = EventType.START,
    parent_event_ids: tuple[str, ...] = (),
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=event_type,
        timestamp=timestamp,
        sequence_number=sequence_number,
        service_id="SERVICE-A",
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        host_id="HOST-A",
        address="10.0.0.10",
        authority_role="PRIMARY",
        parent_event_ids=parent_event_ids,
    )


def test_validator_accepts_fresh_event() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(seconds=30),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
        future_tolerance=timedelta(seconds=5),
    )

    assert validator.validate_event(event, now=REFERENCE_TIME) is True


def test_validator_accepts_event_at_maximum_age_boundary() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(minutes=5),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    assert validator.validate_event(event, now=REFERENCE_TIME) is True


def test_validator_rejects_stale_event() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(minutes=5, seconds=1),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(StaleEventError, match="stale"):
        validator.validate_event(event, now=REFERENCE_TIME)


def test_validator_accepts_timestamp_within_future_tolerance() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME + timedelta(seconds=5),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
        future_tolerance=timedelta(seconds=5),
    )

    assert validator.validate_event(event, now=REFERENCE_TIME) is True


def test_validator_rejects_timestamp_beyond_future_tolerance() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME + timedelta(seconds=6),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
        future_tolerance=timedelta(seconds=5),
    )

    with pytest.raises(FutureTimestampError, match="future"):
        validator.validate_event(event, now=REFERENCE_TIME)


def test_validator_accepts_ordered_transition() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(seconds=20),
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=REFERENCE_TIME - timedelta(seconds=10),
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    assert (
        validator.validate_transition(
            previous,
            current,
            now=REFERENCE_TIME,
        )
        is True
    )


def test_validator_rejects_current_timestamp_before_previous() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(seconds=10),
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=REFERENCE_TIME - timedelta(seconds=20),
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TemporalOrderError, match="timestamp"):
        validator.validate_transition(
            previous,
            current,
            now=REFERENCE_TIME,
        )


def test_validator_rejects_equal_transition_timestamps() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(seconds=10),
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=previous.timestamp,
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TemporalOrderError, match="later"):
        validator.validate_transition(
            previous,
            current,
            now=REFERENCE_TIME,
        )


def test_validator_rejects_non_increasing_sequence() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=2,
        timestamp=REFERENCE_TIME - timedelta(seconds=20),
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=REFERENCE_TIME - timedelta(seconds=10),
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TemporalOrderError, match="sequence"):
        validator.validate_transition(
            previous,
            current,
            now=REFERENCE_TIME,
        )


def test_validator_rejects_naive_event_timestamp() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=datetime(2026, 7, 14, 11, 59, 30),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="timezone-aware"):
        validator.validate_event(event, now=REFERENCE_TIME)


def test_validator_rejects_naive_reference_time() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME - timedelta(seconds=30),
    )

    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="timezone-aware"):
        validator.validate_event(
            event,
            now=datetime(2026, 7, 14, 12, 0),
        )


def test_validator_rejects_invalid_maximum_age() -> None:
    with pytest.raises(ValueError, match="maximum_age"):
        TemporalFreshnessValidator(
            maximum_age=timedelta(seconds=0),
        )


def test_validator_rejects_negative_future_tolerance() -> None:
    with pytest.raises(ValueError, match="future_tolerance"):
        TemporalFreshnessValidator(
            maximum_age=timedelta(minutes=5),
            future_tolerance=timedelta(seconds=-1),
        )


def test_validator_requires_process_event_input() -> None:
    validator = TemporalFreshnessValidator(
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="ProcessEvent"):
        validator.validate_event(
            "EV-001",  # type: ignore[arg-type]
            now=REFERENCE_TIME,
        )