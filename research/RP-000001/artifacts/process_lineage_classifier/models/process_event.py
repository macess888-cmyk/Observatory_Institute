from dataclasses import dataclass
from datetime import datetime

from enums import EventType


@dataclass(frozen=True)
class ProcessEvent:
    """Immutable process-lineage event for prototype version 0.1."""

    event_id: str
    event_type: EventType
    timestamp: datetime
    sequence_number: int

    service_id: str
    runtime_id: str
    execution_id: str
    state_id: str
    host_id: str
    address: str
    authority_role: str

    parent_event_ids: tuple[str, ...] = ()
    parent_state_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()

    migration_id: str | None = None
    snapshot_id: str | None = None
    branch_id: str | None = None
    merge_id: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        required_text_fields = {
            "event_id": self.event_id,
            "service_id": self.service_id,
            "runtime_id": self.runtime_id,
            "execution_id": self.execution_id,
            "state_id": self.state_id,
            "host_id": self.host_id,
            "address": self.address,
            "authority_role": self.authority_role,
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if not isinstance(self.event_type, EventType):
            raise TypeError("event_type must be an EventType.")

        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime.")

        if not isinstance(self.sequence_number, int):
            raise TypeError("sequence_number must be an integer.")

        if self.sequence_number < 0:
            raise ValueError("sequence_number must be non-negative.")

        tuple_fields = {
            "parent_event_ids": self.parent_event_ids,
            "parent_state_ids": self.parent_state_ids,
            "evidence_ids": self.evidence_ids,
        }

        for field_name, values in tuple_fields.items():
            if not isinstance(values, tuple):
                raise TypeError(f"{field_name} must be a tuple.")

            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(
                    f"{field_name} must contain only non-empty strings."
                )