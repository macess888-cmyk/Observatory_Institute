from datetime import datetime, timedelta, timezone

import pytest

from models import WitnessEvidence
from services.witness_evidence_validator import (
    ConflictingWitnessError,
    DuplicateWitnessError,
    InsufficientWitnessesError,
    InvalidWitnessEvidenceError,
    WitnessEvidenceValidator,
)


REFERENCE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_witness(
    *,
    witness_id: str,
    source_id: str,
    claim: str = "PRIMARY_DEACTIVATED",
    subject_event_id: str = "EV-001",
    observed_at: datetime = REFERENCE_TIME,
    provenance_id: str | None = None,
    signature_id: str | None = None,
) -> WitnessEvidence:
    return WitnessEvidence(
        witness_id=witness_id,
        source_id=source_id,
        subject_event_id=subject_event_id,
        claim=claim,
        observed_at=observed_at,
        provenance_id=(
            provenance_id
            if provenance_id is not None
            else f"PROV-{witness_id}"
        ),
        signature_id=(
            signature_id
            if signature_id is not None
            else f"SIG-{witness_id}"
        ),
    )


def test_validator_accepts_independent_witness_quorum() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    assert (
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )
        is True
    )


def test_validator_accepts_more_than_minimum_quorum() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
        ),
        make_witness(
            witness_id="WIT-003",
            source_id="SOURCE-C",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    assert (
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )
        is True
    )


def test_validator_rejects_insufficient_witnesses() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InsufficientWitnessesError,
        match="minimum",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_duplicate_witness_identity() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        DuplicateWitnessError,
        match="witness identity",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_duplicate_source_identity() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-A",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        DuplicateWitnessError,
        match="source identity",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_conflicting_witness_claims() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            claim="PRIMARY_DEACTIVATED",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
            claim="PRIMARY_ACTIVE",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        ConflictingWitnessError,
        match="conflicting",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_self_witnessing_only() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-PRIMARY",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-PRIMARY",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InsufficientWitnessesError,
        match="independent",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_ignores_self_witness_when_independent_quorum_exists() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-PRIMARY",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-003",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    assert (
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )
        is True
    )


def test_validator_rejects_wrong_subject_event() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            subject_event_id="EV-999",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
            subject_event_id="EV-999",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InvalidWitnessEvidenceError,
        match="subject event",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_missing_provenance() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            provenance_id="",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InvalidWitnessEvidenceError,
        match="provenance",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_missing_signature() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            signature_id="",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InvalidWitnessEvidenceError,
        match="signature",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_stale_witness() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            observed_at=REFERENCE_TIME - timedelta(minutes=5, seconds=1),
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InvalidWitnessEvidenceError,
        match="stale",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_future_witness_timestamp() -> None:
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            observed_at=REFERENCE_TIME + timedelta(seconds=1),
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-B",
        ),
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(
        InvalidWitnessEvidenceError,
        match="future",
    ):
        validator.validate(
            witnesses,
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_non_tuple_input() -> None:
    witness = make_witness(
        witness_id="WIT-001",
        source_id="SOURCE-A",
    )

    validator = WitnessEvidenceValidator(
        minimum_witnesses=2,
        maximum_age=timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="tuple"):
        validator.validate(
            [witness],  # type: ignore[arg-type]
            required_claim="PRIMARY_DEACTIVATED",
            subject_event_id="EV-001",
            claimant_source_id="SOURCE-PRIMARY",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_invalid_minimum_witnesses() -> None:
    with pytest.raises(ValueError, match="minimum_witnesses"):
        WitnessEvidenceValidator(
            minimum_witnesses=0,
            maximum_age=timedelta(minutes=5),
        )


def test_validator_rejects_invalid_maximum_age() -> None:
    with pytest.raises(ValueError, match="maximum_age"):
        WitnessEvidenceValidator(
            minimum_witnesses=2,
            maximum_age=timedelta(0),
        )