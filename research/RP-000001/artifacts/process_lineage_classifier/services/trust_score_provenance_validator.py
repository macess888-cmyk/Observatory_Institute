from datetime import datetime

from models import (
    TrustScoreProvenance,
    WitnessTrustProfile,
    WitnessTrustScore,
)


class TrustScoreProvenanceError(ValueError):
    """Raised when trust-score provenance fails validation."""


class TrustScoreProvenanceValidator:
    """Validates trust-score provenance against its profile and score."""

    def validate(
        self,
        provenance: TrustScoreProvenance,
        profile: WitnessTrustProfile,
        score: WitnessTrustScore,
        *,
        expected_profile_id: str,
        expected_scorer_version: str,
        expected_policy_id: str,
        expected_policy_hash: str,
        now: datetime,
    ) -> bool:
        if not isinstance(provenance, TrustScoreProvenance):
            raise TypeError(
                "provenance must be a TrustScoreProvenance."
            )

        if not isinstance(profile, WitnessTrustProfile):
            raise TypeError(
                "profile must be a WitnessTrustProfile."
            )

        if not isinstance(score, WitnessTrustScore):
            raise TypeError(
                "score must be a WitnessTrustScore."
            )

        self._require_non_empty(
            expected_profile_id,
            "expected_profile_id",
        )
        self._require_non_empty(
            expected_scorer_version,
            "expected_scorer_version",
        )
        self._require_non_empty(
            expected_policy_id,
            "expected_policy_id",
        )
        self._require_non_empty(
            expected_policy_hash,
            "expected_policy_hash",
        )
        self._require_timezone_aware(now)

        if provenance.source_id != profile.source_id:
            raise TrustScoreProvenanceError(
                "Trust provenance contains a source identity mismatch."
            )

        if score.source_id != provenance.source_id:
            raise TrustScoreProvenanceError(
                "Trust score source does not match provenance."
            )

        if provenance.profile_id != expected_profile_id:
            raise TrustScoreProvenanceError(
                "Trust provenance contains a profile identity mismatch."
            )

        if provenance.scorer_version != expected_scorer_version:
            raise TrustScoreProvenanceError(
                "Trust provenance contains a scorer version mismatch."
            )

        if provenance.scoring_policy_id != expected_policy_id:
            raise TrustScoreProvenanceError(
                "Trust provenance contains a policy identity mismatch."
            )

        if provenance.scoring_policy_hash != expected_policy_hash:
            raise TrustScoreProvenanceError(
                "Trust provenance contains a policy hash mismatch."
            )

        if provenance.generated_at > now:
            raise TrustScoreProvenanceError(
                "Trust-score provenance timestamp is in the future."
            )

        return True

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

    @staticmethod
    def _require_timezone_aware(
        value: datetime,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(
                "now must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise TypeError(
                "now must be timezone-aware."
            )