from datetime import timedelta

from models import ProcessEvent


class ConcurrentEventWindowError(ValueError):
    """Base error for concurrent event-window validation failures."""


class InvalidConcurrentWindowError(ConcurrentEventWindowError):
    """Raised when the event set or concurrent window is invalid."""


class ConcurrentEventConflictError(ConcurrentEventWindowError):
    """Raised when concurrent events produce an authority conflict."""


class ConcurrentEventWindowValidator:
    """Validates event concurrency windows and authority overlap."""

    def __init__(
        self,
        *,
        maximum_window: timedelta,
    ) -> None:
        if not isinstance(maximum_window, timedelta):
            raise TypeError("maximum_window must be a timedelta.")

        if maximum_window <= timedelta(0):
            raise ValueError(
                "maximum_window must be greater than zero."
            )

        self._maximum_window = maximum_window

    @property
    def maximum_window(self) -> timedelta:
        return self._maximum_window

    def validate(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> bool:
        self._validate_input(events)
        self._validate_identities(events)
        self._validate_service_identity(events)
        self._validate_timestamps(events)
        self._validate_window(events)

        return True

    def validate_authority(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> bool:
        self.validate(events)

        primary_events = tuple(
            event
            for event in events
            if event.authority_role == "PRIMARY"
        )

        if len(primary_events) > 1:
            raise ConcurrentEventConflictError(
                "Multiple PRIMARY authority holders exist inside "
                "the concurrent event window."
            )

        return True

    def _validate_input(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        if not isinstance(events, tuple):
            raise TypeError("events must be a tuple.")

        if any(
            not isinstance(event, ProcessEvent)
            for event in events
        ):
            raise TypeError(
                "events must contain only ProcessEvent instances."
            )

        if len(events) < 2:
            raise InvalidConcurrentWindowError(
                "Concurrent event validation requires at least two events."
            )

    def _validate_identities(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        event_ids = [
            event.event_id
            for event in events
        ]

        if len(set(event_ids)) != len(event_ids):
            raise InvalidConcurrentWindowError(
                "Duplicate event identity detected."
            )

        runtime_ids = [
            event.runtime_id
            for event in events
        ]

        if len(set(runtime_ids)) != len(runtime_ids):
            raise InvalidConcurrentWindowError(
                "Duplicate runtime identity detected."
            )

        execution_ids = [
            event.execution_id
            for event in events
        ]

        if len(set(execution_ids)) != len(execution_ids):
            raise InvalidConcurrentWindowError(
                "Duplicate execution identity detected."
            )

    def _validate_service_identity(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        service_ids = {
            event.service_id
            for event in events
        }

        if len(service_ids) != 1:
            raise InvalidConcurrentWindowError(
                "All events must share one service identity."
            )

    def _validate_timestamps(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        for event in events:
            timestamp = event.timestamp

            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise TypeError(
                    "Event timestamps must be timezone-aware."
                )

    def _validate_window(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        timestamps = [
            event.timestamp
            for event in events
        ]

        earliest = min(timestamps)
        latest = max(timestamps)

        if latest - earliest > self._maximum_window:
            raise InvalidConcurrentWindowError(
                "Events exceed the permitted concurrent window."
            )