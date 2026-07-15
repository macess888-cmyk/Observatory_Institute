from dataclasses import dataclass

from enums import WitnessTrustLevel


@dataclass(frozen=True, slots=True)
class WitnessTrustScore:
    """Immutable trust-scoring result for a witness source."""

    source_id: str
    level: WitnessTrustLevel
    score: int
    verified_observations: int
    contradicted_observations: int
    stale_observations: int
    signature_failures: int
    provenance_failures: int
    independent_confirmations: int
    disqualifying_failures: tuple[str, ...]
    applied_rules: tuple[str, ...]
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str):
            raise TypeError("source_id must be a string.")

        if not self.source_id.strip():
            raise ValueError("source_id must not be empty.")

        if not isinstance(self.level, WitnessTrustLevel):
            raise TypeError(
                "level must be a WitnessTrustLevel."
            )

        if not isinstance(self.score, int):
            raise TypeError("score must be an integer.")

        if not 0 <= self.score <= 100:
            raise ValueError(
                "score must be between 0 and 100."
            )

        for field_name, value in (
            (
                "verified_observations",
                self.verified_observations,
            ),
            (
                "contradicted_observations",
                self.contradicted_observations,
            ),
            (
                "stale_observations",
                self.stale_observations,
            ),
            (
                "signature_failures",
                self.signature_failures,
            ),
            (
                "provenance_failures",
                self.provenance_failures,
            ),
            (
                "independent_confirmations",
                self.independent_confirmations,
            ),
        ):
            if not isinstance(value, int):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

            if value < 0:
                raise ValueError(
                    f"{field_name} must not be negative."
                )

        for field_name, values in (
            (
                "disqualifying_failures",
                self.disqualifying_failures,
            ),
            ("applied_rules", self.applied_rules),
            ("reasons", self.reasons),
        ):
            if not isinstance(values, tuple):
                raise TypeError(
                    f"{field_name} must be a tuple."
                )

            if any(
                not isinstance(value, str)
                for value in values
            ):
                raise TypeError(
                    f"{field_name} must contain only strings."
                )