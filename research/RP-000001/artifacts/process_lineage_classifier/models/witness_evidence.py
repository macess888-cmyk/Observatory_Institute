from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WitnessEvidence:
    """Immutable evidence supplied by an independent witness."""

    witness_id: str
    source_id: str
    subject_event_id: str
    claim: str
    observed_at: datetime
    provenance_id: str
    signature_id: str

    def __post_init__(self) -> None:
        self._require_non_empty(self.witness_id, "witness_id")
        self._require_non_empty(self.source_id, "source_id")
        self._require_non_empty(
            self.subject_event_id,
            "subject_event_id",
        )
        self._require_non_empty(self.claim, "claim")

        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime.")

        if (
            self.observed_at.tzinfo is None
            or self.observed_at.utcoffset() is None
        ):
            raise ValueError(
                "observed_at must be timezone-aware."
            )

        if not isinstance(self.provenance_id, str):
            raise TypeError("provenance_id must be a string.")

        if not isinstance(self.signature_id, str):
            raise TypeError("signature_id must be a string.")

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")