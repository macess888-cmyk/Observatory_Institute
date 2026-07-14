from models import ProcessEvent


class InvalidEventError(ValueError):
    """Raised when an event collection violates structural rules."""


class DuplicateEventError(InvalidEventError):
    """Raised when multiple events use the same event identifier."""


class MissingParentError(InvalidEventError):
    """Raised when an event references a parent that is not present."""


class TransitionValidator:
    """Validates immutable process-event collections."""

    def validate(self, events: tuple[ProcessEvent, ...]) -> bool:
        if not isinstance(events, tuple):
            raise TypeError("events must be a tuple.")

        if not events:
            raise InvalidEventError(
                "events must contain at least one ProcessEvent."
            )

        for event in events:
            if not isinstance(event, ProcessEvent):
                raise TypeError(
                    "events must contain only ProcessEvent instances."
                )

        events_by_id: dict[str, ProcessEvent] = {}

        for event in events:
            if event.event_id in events_by_id:
                raise DuplicateEventError(
                    f"Duplicate event_id detected: {event.event_id}."
                )

            events_by_id[event.event_id] = event

        for event in events:
            if event.event_id in event.parent_event_ids:
                raise InvalidEventError(
                    f"Event {event.event_id} cannot be its own parent."
                )

            for parent_event_id in event.parent_event_ids:
                parent = events_by_id.get(parent_event_id)

                if parent is None:
                    raise MissingParentError(
                        f"Missing parent event: {parent_event_id}."
                    )

                if event.sequence_number <= parent.sequence_number:
                    raise InvalidEventError(
                        "Child event sequence must be greater than "
                        f"parent sequence: {event.event_id}."
                    )

        return True