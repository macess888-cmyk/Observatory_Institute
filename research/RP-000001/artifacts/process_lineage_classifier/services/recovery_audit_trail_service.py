from datetime import datetime

from models import (
    RecoveryAuditEvent,
    RecoveryAuditTrail,
)


class RecoveryAuditTrailAssemblyError(ValueError):
    """Raised when a recovery audit trail cannot be assembled."""


class RecoveryAuditTrailService:
    """Assembles immutable ordered recovery audit trails."""

    def assemble(
        self,
        *,
        trail_id: str,
        subject_id: str,
        events: tuple[RecoveryAuditEvent, ...],
        created_at: datetime,
        issuer_id: str,
    ) -> RecoveryAuditTrail:
        self._require_non_empty(trail_id, "trail_id")
        self._require_non_empty(subject_id, "subject_id")
        self._require_non_empty(issuer_id, "issuer_id")

        self._validate_events(events)
        self._validate_created_at(
            created_at,
            last_event=events[-1],
        )

        return RecoveryAuditTrail(
            trail_id=trail_id,
            subject_id=subject_id,
            events=events,
            created_at=created_at,
            issuer_id=issuer_id,
            execution_requested=False,
            side_effects_permitted=False,
        )

    def _validate_events(
        self,
        events: tuple[RecoveryAuditEvent, ...],
    ) -> None:
        if not isinstance(events, tuple):
            raise TypeError("events must be a tuple.")

        if not events:
            raise RecoveryAuditTrailAssemblyError(
                "Audit trail assembly requires at least one event."
            )

        if any(
            not isinstance(event, RecoveryAuditEvent)
            for event in events
        ):
            raise TypeError(
                "events must contain only RecoveryAuditEvent instances."
            )

        event_ids = tuple(event.event_id for event in events)

        if len(set(event_ids)) != len(event_ids):
            raise RecoveryAuditTrailAssemblyError(
                "duplicate event identity detected."
            )

        sequence_numbers = tuple(
            event.sequence_number
            for event in events
        )

        if len(set(sequence_numbers)) != len(sequence_numbers):
            raise RecoveryAuditTrailAssemblyError(
                "duplicate sequence number detected."
            )

        if sequence_numbers != tuple(sorted(sequence_numbers)):
            raise RecoveryAuditTrailAssemblyError(
                "Events must have increasing sequence numbers."
            )

        timestamps = tuple(
            event.occurred_at
            for event in events
        )

        if timestamps != tuple(sorted(timestamps)):
            raise RecoveryAuditTrailAssemblyError(
                "Events must have increasing timestamps."
            )

    @staticmethod
    def _validate_created_at(
        created_at: datetime,
        *,
        last_event: RecoveryAuditEvent,
    ) -> None:
        if not isinstance(created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise RecoveryAuditTrailAssemblyError(
                "created_at must be timezone-aware."
            )

        if created_at < last_event.occurred_at:
            raise RecoveryAuditTrailAssemblyError(
                "created_at cannot be before the last event."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        if not value.strip():
            raise RecoveryAuditTrailAssemblyError(
                f"{field_name} must not be empty."
            )