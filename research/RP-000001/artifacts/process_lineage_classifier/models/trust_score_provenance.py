from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TrustScoreProvenance:
    """Immutable observer-only provenance for a witness trust score."""

    provenance_id: str
    source_id: str
    profile_id: str
    scorer_version: str
    scoring_policy_id: str
    scoring_policy_hash: str
    generated_at: datetime
    issuer_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(
            self.provenance_id,
            "provenance_id",
        )
        self._require_non_empty(self.source_id, "source_id")
        self._require_non_empty(self.profile_id, "profile_id")
        self._require_non_empty(
            self.scorer_version,
            "scorer_version",
        )
        self._require_non_empty(
            self.scoring_policy_id,
            "scoring_policy_id",
        )
        self._require_non_empty(
            self.scoring_policy_hash,
            "scoring_policy_hash",
        )
        self._require_non_empty(self.issuer_id, "issuer_id")

        if not isinstance(self.generated_at, datetime):
            raise TypeError(
                "generated_at must be a datetime."
            )

        if (
            self.generated_at.tzinfo is None
            or self.generated_at.utcoffset() is None
        ):
            raise ValueError(
                "generated_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "TrustScoreProvenance must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "TrustScoreProvenance must not permit side effects."
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