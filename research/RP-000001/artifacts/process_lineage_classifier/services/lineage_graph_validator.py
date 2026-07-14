from collections import defaultdict

from enums import EventType
from models import ProcessEvent


class InvalidLineageError(ValueError):
    """Raised when lineage structure violates required constraints."""


class LineageCycleError(InvalidLineageError):
    """Raised when a derivation cycle is detected."""


class LineageGraphValidator:
    """Validates process-event derivation structure."""

    def validate(self, events: tuple[ProcessEvent, ...]) -> bool:
        if not isinstance(events, tuple):
            raise TypeError("events must be a tuple.")

        for event in events:
            if not isinstance(event, ProcessEvent):
                raise TypeError(
                    "events must contain only ProcessEvent instances."
                )

        events_by_id = {
            event.event_id: event
            for event in events
        }

        self._detect_cycles(events_by_id)
        self._validate_merges(events)
        self._validate_branches(events)

        return True

    def _detect_cycles(
        self,
        events_by_id: dict[str, ProcessEvent],
    ) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(event_id: str) -> None:
            if event_id in visiting:
                raise LineageCycleError(
                    f"Lineage cycle detected at event {event_id}."
                )

            if event_id in visited:
                return

            event = events_by_id.get(event_id)

            if event is None:
                return

            visiting.add(event_id)

            for parent_event_id in event.parent_event_ids:
                visit(parent_event_id)

            visiting.remove(event_id)
            visited.add(event_id)

        for event_id in events_by_id:
            visit(event_id)

    def _validate_merges(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        for event in events:
            if event.event_type is not EventType.MERGE:
                continue

            if len(event.parent_event_ids) < 2:
                raise InvalidLineageError(
                    "A merge must reference at least two parent events."
                )

            if len(event.parent_state_ids) < 2:
                raise InvalidLineageError(
                    "A merge must reference at least two parent states."
                )

            if len(set(event.parent_event_ids)) < 2:
                raise InvalidLineageError(
                    "A merge must reference distinct parent events."
                )

            if len(set(event.parent_state_ids)) < 2:
                raise InvalidLineageError(
                    "A merge must reference distinct parent states."
                )

            if event.state_id in event.parent_state_ids:
                raise InvalidLineageError(
                    "A merge must create a new state identity."
                )

    def _validate_branches(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        branch_children: dict[str, list[ProcessEvent]] = defaultdict(list)

        for event in events:
            if event.event_type is not EventType.BRANCH:
                continue

            if len(event.parent_event_ids) != 1:
                raise InvalidLineageError(
                    "A branch child must reference exactly one parent event."
                )

            parent_event_id = event.parent_event_ids[0]
            branch_children[parent_event_id].append(event)

        for children in branch_children.values():
            if len(children) < 2:
                raise InvalidLineageError(
                    "A branch must contain at least two child lineages."
                )

            runtime_ids = {
                child.runtime_id
                for child in children
            }
            execution_ids = {
                child.execution_id
                for child in children
            }

            if len(runtime_ids) != len(children):
                raise InvalidLineageError(
                    "Branch children must have distinct runtime identities."
                )

            if len(execution_ids) != len(children):
                raise InvalidLineageError(
                    "Branch children must have distinct execution identities."
                )