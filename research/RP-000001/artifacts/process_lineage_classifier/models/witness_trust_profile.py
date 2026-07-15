from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WitnessTrustProfile:
    """Immutable observation history for a witness source."""

    source_id: str
    verified_observations: int
    contradicted_observations: int
    stale_observations: int
    signature_failures: int
    provenance_failures: int
    independent_confirmations: int

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str):
            raise TypeError("source_id must be a string.")

        if not self.source_id.strip():
            raise ValueError("source_id must not be empty.")

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