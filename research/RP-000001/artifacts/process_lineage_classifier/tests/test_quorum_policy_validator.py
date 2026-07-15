from datetime import datetime, timedelta, timezone

import pytest

from models import QuorumPolicy, WitnessEvidence
from services.quorum_policy_validator import (
    QuorumPolicyValidationError,
    QuorumPolicyValidator,
)


REFERENCE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_policy(
    *,
    policy_id: str = "QP-001",
    minimum_witnesses: int = 2,
    minimum_trusted_witnesses: int = 1,
    maximum_evidence_age: timedelta = timedelta(minutes=5),
    required_claim: str = "PRIMARY_DEACTIVATED",
    permitted_source_ids: tuple[str, ...] = (
        "SOURCE-A",
        "SOURCE-B",
        "SOURCE-C",
    ),
    trusted_source_ids: tuple[str, ...] = (
        "SOURCE-A",
        "SOURCE-B",
    ),
) -> QuorumPolicy:
    return QuorumPolicy(
        policy_id=policy_id,
        minimum_witnesses=minimum_witnesses,
        minimum_trusted_witnesses=minimum_trusted_witnesses,
        maximum_evidence_age=maximum_evidence_age,
        required_claim=required_claim,
        permitted_source_ids=permitted_source_ids,
        trusted_source_ids=trusted_source_ids,
    )


def make_witness(
    *,
    witness_id: str,
    source_id: str,
    claim: str = "PRIMARY_DEACTIVATED",
    subject_event_id: str = "EV-001",
    observed_at: datetime = REFERENCE_TIME,
) -> WitnessEvidence:
    return WitnessEvidence(
        witness_id=witness_id,
        source_id=source_id,
        subject_event_id=subject_event_id,
        claim=claim,
        observed_at=observed_at,
        provenance_id=f"PROV-{witness_id}",
        signature_id=f"SIG-{witness_id}",
    )


def make_valid_witnesses() -> tuple[WitnessEvidence, ...]:
    return (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-C",
        ),
    )


def test_validator_accepts_policy_satisfying_quorum() -> None:
    policy = make_policy()
    witnesses = make_valid_witnesses()

    assert (
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )
        is True
    )


def test_validator_accepts_more_than_required_quorum() -> None:
    policy = make_policy()
    witnesses = make_valid_witnesses() + (
        make_witness(
            witness_id="WIT-003",
            source_id="SOURCE-B",
        ),
    )

    assert (
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )
        is True
    )


def test_validator_rejects_insufficient_total_witnesses() -> None:
    policy = make_policy(minimum_witnesses=2)
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="minimum witness",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_insufficient_trusted_witnesses() -> None:
    policy = make_policy(
        minimum_witnesses=2,
        minimum_trusted_witnesses=1,
        permitted_source_ids=(
            "SOURCE-A",
            "SOURCE-B",
            "SOURCE-C",
            "SOURCE-D",
        ),
        trusted_source_ids=(
            "SOURCE-A",
            "SOURCE-B",
        ),
    )

    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-C",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-D",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="trusted",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_unpermitted_source() -> None:
    policy = make_policy()
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-X",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="permitted",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_wrong_claim() -> None:
    policy = make_policy()
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-C",
            claim="PRIMARY_ACTIVE",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="claim",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_wrong_subject_event() -> None:
    policy = make_policy()
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            subject_event_id="EV-999",
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-C",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="subject event",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_stale_witness() -> None:
    policy = make_policy(
        maximum_evidence_age=timedelta(minutes=5),
    )
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            observed_at=REFERENCE_TIME - timedelta(minutes=6),
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-C",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="stale",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_future_witness() -> None:
    policy = make_policy()
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
            observed_at=REFERENCE_TIME + timedelta(seconds=1),
        ),
        make_witness(
            witness_id="WIT-002",
            source_id="SOURCE-C",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="future",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_duplicate_witness_identity() -> None:
    policy = make_policy()
    witnesses = (
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-A",
        ),
        make_witness(
            witness_id="WIT-001",
            source_id="SOURCE-C",
        ),
    )

    with pytest.raises(
        QuorumPolicyValidationError,
        match="witness identity",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_duplicate_source_identity() -> None:
    policy = make_policy()
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

    with pytest.raises(
        QuorumPolicyValidationError,
        match="source identity",
    ):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_non_tuple_witnesses() -> None:
    policy = make_policy()
    witnesses = make_valid_witnesses()

    with pytest.raises(TypeError, match="tuple"):
        QuorumPolicyValidator().validate(
            policy,
            list(witnesses),  # type: ignore[arg-type]
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_non_witness_member() -> None:
    policy = make_policy()
    witness = make_valid_witnesses()[0]

    with pytest.raises(TypeError, match="WitnessEvidence"):
        QuorumPolicyValidator().validate(
            policy,
            (witness, "WIT-002"),  # type: ignore[arg-type]
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_requires_quorum_policy() -> None:
    witnesses = make_valid_witnesses()

    with pytest.raises(TypeError, match="QuorumPolicy"):
        QuorumPolicyValidator().validate(
            "QP-001",  # type: ignore[arg-type]
            witnesses,
            subject_event_id="EV-001",
            now=REFERENCE_TIME,
        )


def test_validator_rejects_naive_reference_time() -> None:
    policy = make_policy()
    witnesses = make_valid_witnesses()

    with pytest.raises(TypeError, match="timezone-aware"):
        QuorumPolicyValidator().validate(
            policy,
            witnesses,
            subject_event_id="EV-001",
            now=datetime(2026, 7, 14, 12, 0),
        )