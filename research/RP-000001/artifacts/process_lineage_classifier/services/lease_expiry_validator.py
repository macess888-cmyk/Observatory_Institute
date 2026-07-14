from datetime import datetime

from models import ProcessEvent


class LeaseValidationError(ValueError):
    """Base error for lease validation failures."""


class InvalidLeaseError(LeaseValidationError):
    """Raised when the lease interval is structurally invalid."""


class LeaseNotYetActiveError(LeaseValidationError):
    """Raised when validation occurs before the lease start time."""


class ExpiredLeaseError(LeaseValidationError):
    """Raised when validation occurs at or after lease expiry."""


class LeaseExpiryValidator:
    """Validates whether an event is operating within an active lease."""

    def __init__(
        self,
        *,
        lease_started_at: datetime,
        lease_expires_at: datetime,
    ) -> None:
        self._require_timezone_aware(
            lease_started_at,
            field_name="lease_started_at",
        )
        self._require_timezone_aware(
            lease_expires_at,
            field_name="lease_expires_at",
        )

        if lease_expires_at <= lease_started_at:
            raise InvalidLeaseError(
                "lease_expires_at must be after lease_started_at."
            )

        self._lease_started_at = lease_started_at
        self._lease_expires_at = lease_expires_at

    @property
    def lease_started_at(self) -> datetime:
        return self._lease_started_at

    @property
    def lease_expires_at(self) -> datetime:
        return self._lease_expires_at

    def validate(
        self,
        event: ProcessEvent,
        *,
        now: datetime,
    ) -> bool:
        if not isinstance(event, ProcessEvent):
            raise TypeError("event must be a ProcessEvent.")

        self._require_timezone_aware(
            now,
            field_name="reference time",
        )

        if now < self._lease_started_at:
            raise LeaseNotYetActiveError(
                "Lease is not yet active."
            )

        if now >= self._lease_expires_at:
            if event.authority_role == "PRIMARY":
                raise ExpiredLeaseError(
                    "Lease expired; PRIMARY authority is no longer valid."
                )

            raise ExpiredLeaseError(
                "Lease expired."
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