from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class QuorumPolicy:
    """Immutable policy for evaluating witness quorum sufficiency."""

    policy_id: str
    minimum_witnesses: int
    minimum_trusted_witnesses: int
    maximum_evidence_age: timedelta
    required_claim: str
    permitted_source_ids: tuple[str, ...]
    trusted_source_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        self._require_non_empty(self.policy_id, "policy_id")
        self._require_non_empty(self.required_claim, "required_claim")

        if not isinstance(self.minimum_witnesses, int):
            raise TypeError(
                "minimum_witnesses must be an integer."
            )

        if self.minimum_witnesses < 1:
            raise ValueError(
                "minimum_witnesses must be greater than zero."
            )

        if not isinstance(
            self.minimum_trusted_witnesses,
            int,
        ):
            raise TypeError(
                "minimum_trusted_witnesses must be an integer."
            )

        if self.minimum_trusted_witnesses < 0:
            raise ValueError(
                "minimum_trusted_witnesses must not be negative."
            )

        if (
            self.minimum_trusted_witnesses
            > self.minimum_witnesses
        ):
            raise ValueError(
                "minimum_trusted_witnesses cannot exceed "
                "minimum_witnesses."
            )

        if not isinstance(
            self.maximum_evidence_age,
            timedelta,
        ):
            raise TypeError(
                "maximum_evidence_age must be a timedelta."
            )

        if self.maximum_evidence_age <= timedelta(0):
            raise ValueError(
                "maximum_evidence_age must be greater than zero."
            )

        self._require_string_tuple(
            self.permitted_source_ids,
            "permitted_source_ids",
        )
        self._require_string_tuple(
            self.trusted_source_ids,
            "trusted_source_ids",
        )

        if not self.permitted_source_ids:
            raise ValueError(
                "permitted_source_ids must not be empty."
            )

        if (
            len(set(self.permitted_source_ids))
            != len(self.permitted_source_ids)
        ):
            raise ValueError(
                "permitted_source_ids must be unique."
            )

        if (
            len(set(self.trusted_source_ids))
            != len(self.trusted_source_ids)
        ):
            raise ValueError(
                "trusted_source_ids must be unique."
            )

        unpermitted_trusted_sources = tuple(
            source_id
            for source_id in self.trusted_source_ids
            if source_id not in self.permitted_source_ids
        )

        if unpermitted_trusted_sources:
            raise ValueError(
                "trusted_source_ids must also be permitted."
            )

        if (
            self.minimum_witnesses
            > len(self.permitted_source_ids)
        ):
            raise ValueError(
                "minimum_witnesses cannot exceed the number "
                "of permitted sources."
            )

        if (
            self.minimum_trusted_witnesses
            > len(self.trusted_source_ids)
        ):
            raise ValueError(
                "minimum_trusted_witnesses cannot exceed the "
                "number of trusted sources."
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

    @staticmethod
    def _require_string_tuple(
        value: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field_name} must be a tuple."
            )

        if any(
            not isinstance(item, str)
            for item in value
        ):
            raise TypeError(
                f"{field_name} must contain only strings."
            )

        if any(
            not item.strip()
            for item in value
        ):
            raise ValueError(
                f"{field_name} must not contain empty values."
            )