from dataclasses import dataclass


@dataclass(frozen=True)
class TransitionEvidence:
    """Immutable transition evidence for prototype version 0.1."""

    evidence_id: str
    evidence_type: str
    source_event_id: str
    target_event_id: str
    is_verified: bool

    checksum: str | None = None
    source: str | None = None
    method: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        required_text_fields = {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "source_event_id": self.source_event_id,
            "target_event_id": self.target_event_id,
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if not isinstance(self.is_verified, bool):
            raise TypeError("is_verified must be a boolean.")

        optional_text_fields = {
            "checksum": self.checksum,
            "source": self.source,
            "method": self.method,
            "notes": self.notes,
        }

        for field_name, value in optional_text_fields.items():
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(
                    f"{field_name} must be None or a non-empty string."
                )