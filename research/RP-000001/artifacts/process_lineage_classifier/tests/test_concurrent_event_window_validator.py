from datetime import datetime, timedelta, timezone

import pytest

from enums import EventType
from models import ProcessEvent
from services.concurrent_event_window_validator import (
    ConcurrentEventConflictError,
    ConcurrentEventWindowValidator,
    InvalidConcurrentWindowError,
)


REFERENCE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    timestamp: datetime,
    runtime_id: str,
    execution_id: str,
    state_id: str,
    authority_role: str = "PRIMARY",
    service_id: str = "SERVICE-A",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=EventType.START,
        timestamp=timestamp,
        sequence_number=sequence_number,
        service_id=service_id,
        runtime_id=runtime_id,
        execution_id=execution_id,
        state_id=state_id,
        host_id=f"HOST-{runtime_id}",
        address=f"10.0.0.{sequence_number}",
        authority_role=authority_role,
    )


def make_concurrent_pair() -> tuple[ProcessEvent, ProcessEvent]:
    first = make_event(
        event_id="EV-001",
        sequence_number=1,
        timestamp=REFERENCE_TIME,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
    )
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=REFERENCE_TIME + timedelta(milliseconds=500),
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
    )
    return first, second


def test_validator_accepts_events_inside_concurrent_window() -> None:
    first, second = make_concurrent_pair()

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    assert validator.validate((first, second)) is True


def test_validator_accepts_exact_window_boundary() -> None:
    first, _ = make_concurrent_pair()
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=REFERENCE_TIME + timedelta(seconds=1),
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    assert validator.validate((first, second)) is True


def test_validator_rejects_events_outside_window() -> None:
    first, _ = make_concurrent_pair()
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        timestamp=REFERENCE_TIME + timedelta(seconds=1, microseconds=1),
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        InvalidConcurrentWindowError,
        match="window",
    ):
        validator.validate((first, second))


def test_validator_detects_concurrent_primary_conflict() -> None:
    first, second = make_concurrent_pair()

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        ConcurrentEventConflictError,
        match="PRIMARY",
    ):
        validator.validate_authority((first, second))


def test_validator_accepts_single_primary_in_window() -> None:
    first, second = make_concurrent_pair()

    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        timestamp=second.timestamp,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        authority_role="SECONDARY",
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    assert validator.validate_authority((first, second)) is True


def test_validator_rejects_mixed_service_identities() -> None:
    first, second = make_concurrent_pair()

    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        timestamp=second.timestamp,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
        service_id="SERVICE-B",
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        InvalidConcurrentWindowError,
        match="service",
    ):
        validator.validate((first, second))


def test_validator_rejects_duplicate_event_identity() -> None:
    first, second = make_concurrent_pair()

    second = make_event(
        event_id=first.event_id,
        sequence_number=second.sequence_number,
        timestamp=second.timestamp,
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        InvalidConcurrentWindowError,
        match="event identity",
    ):
        validator.validate((first, second))


def test_validator_rejects_duplicate_runtime_identity() -> None:
    first, second = make_concurrent_pair()

    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        timestamp=second.timestamp,
        runtime_id=first.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        InvalidConcurrentWindowError,
        match="runtime identity",
    ):
        validator.validate((first, second))


def test_validator_rejects_duplicate_execution_identity() -> None:
    first, second = make_concurrent_pair()

    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        timestamp=second.timestamp,
        runtime_id=second.runtime_id,
        execution_id=first.execution_id,
        state_id=second.state_id,
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        InvalidConcurrentWindowError,
        match="execution identity",
    ):
        validator.validate((first, second))


def test_validator_rejects_non_tuple_input() -> None:
    first, second = make_concurrent_pair()

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(TypeError, match="tuple"):
        validator.validate(
            [first, second]  # type: ignore[arg-type]
        )


def test_validator_rejects_single_event() -> None:
    first, _ = make_concurrent_pair()

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(
        InvalidConcurrentWindowError,
        match="at least two",
    ):
        validator.validate((first,))


def test_validator_rejects_non_process_event_member() -> None:
    first, _ = make_concurrent_pair()

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(TypeError, match="ProcessEvent"):
        validator.validate(
            (first, "EV-002")  # type: ignore[arg-type]
        )


def test_validator_rejects_naive_timestamp() -> None:
    first, second = make_concurrent_pair()

    second = make_event(
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        timestamp=datetime(2026, 7, 14, 12, 0),
        runtime_id=second.runtime_id,
        execution_id=second.execution_id,
        state_id=second.state_id,
    )

    validator = ConcurrentEventWindowValidator(
        maximum_window=timedelta(seconds=1),
    )

    with pytest.raises(TypeError, match="timezone-aware"):
        validator.validate((first, second))


def test_validator_rejects_invalid_window() -> None:
    with pytest.raises(ValueError, match="maximum_window"):
        ConcurrentEventWindowValidator(
            maximum_window=timedelta(0),
        )