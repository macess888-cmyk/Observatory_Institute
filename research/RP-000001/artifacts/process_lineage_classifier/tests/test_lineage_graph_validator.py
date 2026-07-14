from datetime import datetime, timedelta, timezone

import pytest

from enums import EventType
from models import ProcessEvent
from services.lineage_graph_validator import (
    InvalidLineageError,
    LineageCycleError,
    LineageGraphValidator,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: EventType = EventType.START,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    runtime_id: str | None = None,
    execution_id: str | None = None,
    state_id: str | None = None,
    merge_id: str | None = None,
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=event_type,
        timestamp=datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
        + timedelta(seconds=sequence_number),
        sequence_number=sequence_number,
        service_id="SERVICE-A",
        runtime_id=runtime_id or f"RUNTIME-{sequence_number:03d}",
        execution_id=execution_id or f"EXEC-{sequence_number:03d}",
        state_id=state_id or f"STATE-{sequence_number:03d}",
        host_id="HOST-001",
        address="10.0.0.10",
        authority_role="PRIMARY",
        parent_event_ids=parent_event_ids,
        parent_state_ids=parent_state_ids,
        merge_id=merge_id,
    )


def test_validator_accepts_linear_lineage() -> None:
    first = make_event(
        event_id="EV-001",
        sequence_number=1,
    )
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTART,
        parent_event_ids=("EV-001",),
    )
    third = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.RESTORE,
        parent_event_ids=("EV-002",),
    )

    validator = LineageGraphValidator()

    assert validator.validate((first, second, third)) is True


def test_validator_accepts_valid_branch() -> None:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
        state_id="STATE-001",
    )
    child_a = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.BRANCH,
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
    )
    child_b = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.BRANCH,
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        runtime_id="RUNTIME-B",
        execution_id="EXEC-B",
        state_id="STATE-B",
    )

    validator = LineageGraphValidator()

    assert validator.validate((parent, child_a, child_b)) is True


def test_validator_accepts_valid_merge() -> None:
    parent_a = make_event(
        event_id="EV-001",
        sequence_number=1,
        state_id="STATE-A",
    )
    parent_b = make_event(
        event_id="EV-002",
        sequence_number=2,
        state_id="STATE-B",
    )
    merged = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.MERGE,
        parent_event_ids=("EV-001", "EV-002"),
        parent_state_ids=("STATE-A", "STATE-B"),
        state_id="STATE-M",
        merge_id="MERGE-001",
    )

    validator = LineageGraphValidator()

    assert validator.validate((parent_a, parent_b, merged)) is True


def test_validator_rejects_direct_cycle() -> None:
    first = make_event(
        event_id="EV-001",
        sequence_number=1,
        parent_event_ids=("EV-002",),
    )
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        parent_event_ids=("EV-001",),
    )

    validator = LineageGraphValidator()

    with pytest.raises(LineageCycleError, match="cycle"):
        validator.validate((first, second))


def test_validator_rejects_indirect_cycle() -> None:
    first = make_event(
        event_id="EV-001",
        sequence_number=1,
        parent_event_ids=("EV-003",),
    )
    second = make_event(
        event_id="EV-002",
        sequence_number=2,
        parent_event_ids=("EV-001",),
    )
    third = make_event(
        event_id="EV-003",
        sequence_number=3,
        parent_event_ids=("EV-002",),
    )

    validator = LineageGraphValidator()

    with pytest.raises(LineageCycleError, match="cycle"):
        validator.validate((first, second, third))


def test_validator_rejects_merge_with_one_parent_event() -> None:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
        state_id="STATE-A",
    )
    merged = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MERGE,
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-A",),
        state_id="STATE-M",
        merge_id="MERGE-001",
    )

    validator = LineageGraphValidator()

    with pytest.raises(InvalidLineageError, match="at least two parent"):
        validator.validate((parent, merged))


def test_validator_rejects_merge_without_new_state_identity() -> None:
    parent_a = make_event(
        event_id="EV-001",
        sequence_number=1,
        state_id="STATE-A",
    )
    parent_b = make_event(
        event_id="EV-002",
        sequence_number=2,
        state_id="STATE-B",
    )
    merged = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.MERGE,
        parent_event_ids=("EV-001", "EV-002"),
        parent_state_ids=("STATE-A", "STATE-B"),
        state_id="STATE-A",
        merge_id="MERGE-001",
    )

    validator = LineageGraphValidator()

    with pytest.raises(InvalidLineageError, match="new state identity"):
        validator.validate((parent_a, parent_b, merged))


def test_validator_rejects_branch_with_reused_runtime_identity() -> None:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
        state_id="STATE-001",
    )
    child_a = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.BRANCH,
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        runtime_id="RUNTIME-SHARED",
        execution_id="EXEC-A",
        state_id="STATE-A",
    )
    child_b = make_event(
        event_id="EV-003",
        sequence_number=3,
        event_type=EventType.BRANCH,
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        runtime_id="RUNTIME-SHARED",
        execution_id="EXEC-B",
        state_id="STATE-B",
    )

    validator = LineageGraphValidator()

    with pytest.raises(InvalidLineageError, match="distinct runtime"):
        validator.validate((parent, child_a, child_b))


def test_validator_rejects_branch_with_only_one_child() -> None:
    parent = make_event(
        event_id="EV-001",
        sequence_number=1,
        state_id="STATE-001",
    )
    child = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.BRANCH,
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-A",
    )

    validator = LineageGraphValidator()

    with pytest.raises(InvalidLineageError, match="at least two child"):
        validator.validate((parent, child))


def test_validator_requires_tuple_input() -> None:
    event = make_event(
        event_id="EV-001",
        sequence_number=1,
    )

    validator = LineageGraphValidator()

    with pytest.raises(TypeError, match="tuple"):
        validator.validate([event])  # type: ignore[arg-type]