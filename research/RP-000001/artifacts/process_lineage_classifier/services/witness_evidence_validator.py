from datetime import datetime, timedelta

from models import WitnessEvidence


class WitnessEvidenceValidationError(ValueError):
    """Base error for witness-evidence validation failures."""


class InvalidWitnessEvidenceError(WitnessEvidenceValidationError):
    """Raised when witness evidence is malformed or temporally invalid."""


class DuplicateWitnessError(WitnessEvidenceValidationError):
    """Raised when witness or source identities are duplicated."""


class ConflictingWitnessError(WitnessEvidenceValidationError):
    """Raised when independent witnesses provide conflicting claims."""


class InsufficientWitnessesError(WitnessEvidenceValidationError):
    """Raised when an independent witness quorum is not established."""


class WitnessEvidenceValidator:
    """Validates independent witness evidence and quorum sufficiency."""

    def __init__(
        self,
        *,
        minimum_witnesses: int,
        maximum_age: timedelta,
    ) -> None:
        if not isinstance(minimum_witnesses, int):
            raise TypeError("minimum_witnesses must be an integer.")

        if minimum_witnesses < 1:
            raise ValueError(
                "minimum_witnesses must be greater than zero."
            )

        if not isinstance(maximum_age, timedelta):
            raise TypeError("maximum_age must be a timedelta.")

        if maximum_age <= timedelta(0):
            raise ValueError(
                "maximum_age must be greater than zero."
            )

        self._minimum_witnesses = minimum_witnesses
        self._maximum_age = maximum_age

    @property
    def minimum_witnesses(self) -> int:
        return self._minimum_witnesses

    @property
    def maximum_age(self) -> timedelta:
        return self._maximum_age

    def validate(
        self,
        witnesses: tuple[WitnessEvidence, ...],
        *,
        required_claim: str,
        subject_event_id: str,
        claimant_source_id: str,
        now: datetime,
    ) -> bool:
        if not isinstance(witnesses, tuple):
            raise TypeError("witnesses must be a tuple.")

        if any(
            not isinstance(witness, WitnessEvidence)
            for witness in witnesses
        ):
            raise TypeError(
                "witnesses must contain only WitnessEvidence instances."
            )

        self._require_non_empty(required_claim, "required_claim")
        self._require_non_empty(subject_event_id, "subject_event_id")
        self._require_non_empty(
            claimant_source_id,
            "claimant_source_id",
        )
        self._require_timezone_aware(now, field_name="now")

        self._validate_unique_identities(
            witnesses,
            claimant_source_id=claimant_source_id,
        )
        self._validate_evidence_records(
            witnesses,
            subject_event_id=subject_event_id,
            now=now,
        )
        self._validate_claim_consistency(
            witnesses,
            required_claim=required_claim,
        )

        independent_witnesses = tuple(
            witness
            for witness in witnesses
            if witness.source_id != claimant_source_id
        )

        if len(independent_witnesses) < self._minimum_witnesses:
            raise InsufficientWitnessesError(
                "independent witness count does not satisfy the minimum "
                "witness quorum."
            )

        return True

    def _validate_unique_identities(
        self,
        witnesses: tuple[WitnessEvidence, ...],
        *,
        claimant_source_id: str,
    ) -> None:
        witness_ids = [
            witness.witness_id
            for witness in witnesses
        ]

        if len(set(witness_ids)) != len(witness_ids):
            raise DuplicateWitnessError(
                "Duplicate witness identity detected."
            )

        independent_source_ids = [
            witness.source_id
            for witness in witnesses
            if witness.source_id != claimant_source_id
        ]

        if (
            len(set(independent_source_ids))
            != len(independent_source_ids)
        ):
            raise DuplicateWitnessError(
                "Duplicate source identity detected."
            )

    def _validate_evidence_records(
        self,
        witnesses: tuple[WitnessEvidence, ...],
        *,
        subject_event_id: str,
        now: datetime,
    ) -> None:
        for witness in witnesses:
            if witness.subject_event_id != subject_event_id:
                raise InvalidWitnessEvidenceError(
                    "Witness evidence references the wrong subject event."
                )

            if not witness.provenance_id.strip():
                raise InvalidWitnessEvidenceError(
                    "Witness evidence requires provenance."
                )

            if not witness.signature_id.strip():
                raise InvalidWitnessEvidenceError(
                    "Witness evidence requires a signature."
                )

            self._require_timezone_aware(
                witness.observed_at,
                field_name="observed_at",
            )

            if witness.observed_at > now:
                raise InvalidWitnessEvidenceError(
                    "Witness observation timestamp is in the future."
                )

            if now - witness.observed_at > self._maximum_age:
                raise InvalidWitnessEvidenceError(
                    "Witness evidence is stale."
                )

    def _validate_claim_consistency(
        self,
        witnesses: tuple[WitnessEvidence, ...],
        *,
        required_claim: str,
    ) -> None:
        claims = {
            witness.claim
            for witness in witnesses
        }

        if len(claims) > 1:
            raise ConflictingWitnessError(
                "Witnesses supplied conflicting claims."
            )

        if claims and required_claim not in claims:
            raise ConflictingWitnessError(
                "Witness claim conflicts with the required claim."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")

    @staticmethod
    def _require_timezone_aware(
        value: datetime,
        *,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a datetime.")

        if value.tzinfo is None or value.utcoffset() is None:
            raise TypeError(
                f"{field_name} must be timezone-aware."
            )