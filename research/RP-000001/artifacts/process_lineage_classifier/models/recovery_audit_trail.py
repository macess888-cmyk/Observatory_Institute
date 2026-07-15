from dataclasses import dataclass
from datetime import datetime

from .recovery_audit_event import RecoveryAuditEvent


@dataclass(frozen=True, slots=True)
class RecoveryAuditTrail:
    """Immutable ordered observer-only recovery audit trail."""

    trail_id: str
    subject_id: str
    events: tuple[RecoveryAuditEvent, ...]
    created_at: datetime
    issuer_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.trail_id, "trail_id")
        self._require_non_empty(self.subject_id, "subject_id")
        self._require_non_empty(self.issuer_id, "issuer_id")

        if not isinstance(self.events, tuple):
            raise TypeError("events must be a tuple.")

        if not self.events:
            raise ValueError("events must not be empty.")

        if any(
            not isinstance(event, RecoveryAuditEvent)
            for event in self.events
        ):
            raise TypeError(
                "events must contain only RecoveryAuditEvent instances."
            )

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise ValueError(
                "created_at must be timezone-aware."
            )

        self._validate_event_identities()
        self._validate_sequence_order()
        self._validate_timestamp_order()

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryAuditTrail must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryAuditTrail must not permit side effects."
            )

    def _validate_event_identities(self) -> None:
        event_ids = [
            event.event_id
            for event in self.events
        ]

        if len(set(event_ids)) != len(event_ids):
            raise ValueError(
                "Duplicate event identity detected."
            )

    def _validate_sequence_order(self) -> None:
        sequence_numbers = [
            event.sequence_number
            for event in self.events
        ]

        if len(set(sequence_numbers)) != len(sequence_numbers):
            raise ValueError(
                "Audit event sequence numbers must be unique."
            )

        if sequence_numbers != sorted(sequence_numbers):
            raise ValueError(
                "Audit event sequence numbers must be increasing."
            )

    def _validate_timestamp_order(self) -> None:
        timestamps = [
            event.occurred_at
            for event in self.events
        ]

        if timestamps != sorted(timestamps):
            raise ValueError(
                "Audit event timestamps must be increasing."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be empty."
            )