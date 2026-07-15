from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RecoveryDecisionVerification:
    """Immutable observer-only verification of a recovery decision replay."""

    verification_id: str
    replay_id: str
    original_decision_id: str

    verified: bool
    replay_verified: bool

    status_match: bool
    operational_status_match: bool
    confidence_match: bool
    rules_match: bool
    reasons_match: bool
    missing_evidence_match: bool
    conflicts_match: bool

    verified_at: datetime
    verifier_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(
            self.verification_id,
            "verification_id",
        )
        self._require_non_empty(self.replay_id, "replay_id")
        self._require_non_empty(
            self.original_decision_id,
            "original_decision_id",
        )
        self._require_non_empty(self.verifier_id, "verifier_id")

        for field_name, value in (
            ("verified", self.verified),
            ("replay_verified", self.replay_verified),
            ("status_match", self.status_match),
            (
                "operational_status_match",
                self.operational_status_match,
            ),
            ("confidence_match", self.confidence_match),
            ("rules_match", self.rules_match),
            ("reasons_match", self.reasons_match),
            (
                "missing_evidence_match",
                self.missing_evidence_match,
            ),
            ("conflicts_match", self.conflicts_match),
        ):
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        expected_verified = all(
            (
                self.replay_verified,
                self.status_match,
                self.operational_status_match,
                self.confidence_match,
                self.rules_match,
                self.reasons_match,
                self.missing_evidence_match,
                self.conflicts_match,
            )
        )

        if self.verified is not expected_verified:
            raise ValueError(
                "verified must match the replay verification results."
            )

        if not isinstance(self.verified_at, datetime):
            raise TypeError(
                "verified_at must be a datetime."
            )

        if (
            self.verified_at.tzinfo is None
            or self.verified_at.utcoffset() is None
        ):
            raise ValueError(
                "verified_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryDecisionVerification must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryDecisionVerification must not permit side effects."
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