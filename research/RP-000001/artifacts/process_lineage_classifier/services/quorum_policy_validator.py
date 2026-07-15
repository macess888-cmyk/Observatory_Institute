from datetime import datetime

from models import QuorumPolicy, WitnessEvidence


class QuorumPolicyValidationError(ValueError):
    """Raised when witness evidence does not satisfy quorum policy."""


class QuorumPolicyValidator:
    """Validates witness evidence against an immutable quorum policy."""

    def validate(
        self,
        policy: QuorumPolicy,
        witnesses: tuple[WitnessEvidence, ...],
        *,
        subject_event_id: str,
        now: datetime,
    ) -> bool:
        if not isinstance(policy, QuorumPolicy):
            raise TypeError("policy must be a QuorumPolicy.")

        if not isinstance(witnesses, tuple):
            raise TypeError("witnesses must be a tuple.")

        if any(
            not isinstance(witness, WitnessEvidence)
            for witness in witnesses
        ):
            raise TypeError(
                "witnesses must contain only WitnessEvidence instances."
            )

        self._require_non_empty(
            subject_event_id,
            "subject_event_id",
        )
        self._require_timezone_aware(now)

        self._validate_unique_identities(witnesses)
        self._validate_records(
            policy,
            witnesses,
            subject_event_id=subject_event_id,
            now=now,
        )
        self._validate_quorum(policy, witnesses)

        return True

    def _validate_unique_identities(
        self,
        witnesses: tuple[WitnessEvidence, ...],
    ) -> None:
        witness_ids = [
            witness.witness_id
            for witness in witnesses
        ]

        if len(set(witness_ids)) != len(witness_ids):
            raise QuorumPolicyValidationError(
                "Duplicate witness identity detected."
            )

        source_ids = [
            witness.source_id
            for witness in witnesses
        ]

        if len(set(source_ids)) != len(source_ids):
            raise QuorumPolicyValidationError(
                "Duplicate source identity detected."
            )

    def _validate_records(
        self,
        policy: QuorumPolicy,
        witnesses: tuple[WitnessEvidence, ...],
        *,
        subject_event_id: str,
        now: datetime,
    ) -> None:
        for witness in witnesses:
            if witness.source_id not in policy.permitted_source_ids:
                raise QuorumPolicyValidationError(
                    "Witness source is not permitted by the quorum policy."
                )

            if witness.claim != policy.required_claim:
                raise QuorumPolicyValidationError(
                    "Witness claim does not satisfy the quorum policy."
                )

            if witness.subject_event_id != subject_event_id:
                raise QuorumPolicyValidationError(
                    "Witness references the wrong subject event."
                )

            if witness.observed_at > now:
                raise QuorumPolicyValidationError(
                    "Witness observation timestamp is in the future."
                )

            if (
                now - witness.observed_at
                > policy.maximum_evidence_age
            ):
                raise QuorumPolicyValidationError(
                    "Witness evidence is stale."
                )

    def _validate_quorum(
        self,
        policy: QuorumPolicy,
        witnesses: tuple[WitnessEvidence, ...],
    ) -> None:
        if len(witnesses) < policy.minimum_witnesses:
            raise QuorumPolicyValidationError(
                "Witness count does not satisfy the minimum witness quorum."
            )

        trusted_witness_count = sum(
            witness.source_id in policy.trusted_source_ids
            for witness in witnesses
        )

        if (
            trusted_witness_count
            < policy.minimum_trusted_witnesses
        ):
            raise QuorumPolicyValidationError(
                "Witness set does not satisfy the minimum trusted "
                "witness requirement."
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
    def _require_timezone_aware(
        value: datetime,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError("now must be a datetime.")

        if value.tzinfo is None or value.utcoffset() is None:
            raise TypeError(
                "now must be timezone-aware."
            )