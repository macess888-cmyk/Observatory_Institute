from datetime import datetime, timedelta

from models import ProcessEvent


class TemporalFreshnessError(ValueError):
    """Base error for temporal freshness validation failures."""


class StaleEventError(TemporalFreshnessError):
    """Raised when an event exceeds the permitted maximum age."""


class FutureTimestampError(TemporalFreshnessError):
    """Raised when an event timestamp exceeds future tolerance."""


class TemporalOrderError(TemporalFreshnessError):
    """Raised when transition timestamps or sequences are not ordered."""


class TemporalFreshnessValidator:
    """Validates event freshness and temporal transition ordering."""

    def __init__(
        self,
        *,
        maximum_age: timedelta,
        future_tolerance: timedelta = timedelta(seconds=0),
    ) -> None:
        if not isinstance(maximum_age, timedelta):
            raise TypeError("maximum_age must be a timedelta.")

        if not isinstance(future_tolerance, timedelta):
            raise TypeError("future_tolerance must be a timedelta.")

        if maximum_age <= timedelta(0):
            raise ValueError("maximum_age must be greater than zero.")

        if future_tolerance < timedelta(0):
            raise ValueError(
                "future_tolerance must be zero or greater."
            )

        self._maximum_age = maximum_age
        self._future_tolerance = future_tolerance

    @property
    def maximum_age(self) -> timedelta:
        return self._maximum_age

    @property
    def future_tolerance(self) -> timedelta:
        return self._future_tolerance

    def validate_event(
        self,
        event: ProcessEvent,
        *,
        now: datetime,
    ) -> bool:
        if not isinstance(event, ProcessEvent):
            raise TypeError("event must be a ProcessEvent.")

        self._require_timezone_aware(
            event.timestamp,
            field_name="event timestamp",
        )
        self._require_timezone_aware(
            now,
            field_name="reference time",
        )

        future_limit = now + self._future_tolerance

        if event.timestamp > future_limit:
            raise FutureTimestampError(
                "Event timestamp is beyond the permitted future tolerance."
            )

        age = now - event.timestamp

        if age > self._maximum_age:
            raise StaleEventError(
                "Event is stale and exceeds the permitted maximum age."
            )

        return True

    def validate_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
        *,
        now: datetime,
    ) -> bool:
        if not isinstance(previous, ProcessEvent):
            raise TypeError("previous must be a ProcessEvent.")

        if not isinstance(current, ProcessEvent):
            raise TypeError("current must be a ProcessEvent.")

        self.validate_event(previous, now=now)
        self.validate_event(current, now=now)

        if current.timestamp <= previous.timestamp:
            raise TemporalOrderError(
                "Current timestamp must be later than the previous timestamp."
            )

        if current.sequence_number <= previous.sequence_number:
            raise TemporalOrderError(
                "Current sequence number must be greater than the previous "
                "sequence number."
            )

        return True

    @staticmethod
    def _require_timezone_aware(
        value: datetime,
        *,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a datetime.")

        if value.tzinfo is None or value.utcoffset() is None:
            raise TypeError(
                f"{field_name} must be timezone-aware."
            )