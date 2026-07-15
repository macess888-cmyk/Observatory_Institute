from datetime import datetime, timedelta, timezone

import pytest

from models import PolicyVersionBinding, QuorumPolicy
from services.policy_version_binding_validator import (
    PolicyVersionBindingError,
    PolicyVersionBindingValidator,
)


BOUND_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_policy(
    *,
    policy_id: str = "QP-001",
) -> QuorumPolicy:
    return QuorumPolicy(
        policy_id=policy_id,
        minimum_witnesses=2,
        minimum_trusted_witnesses=1,
        maximum_evidence_age=timedelta(minutes=5),
        required_claim="PRIMARY_DEACTIVATED",
        permitted_source_ids=(
            "SOURCE-A",
            "SOURCE-B",
            "SOURCE-C",
        ),
        trusted_source_ids=(
            "SOURCE-A",
            "SOURCE-B",
        ),
    )


def make_binding(
    *,
    binding_id: str = "PVB-001",
    policy_id: str = "QP-001",
    policy_version: str = "1.0.0",
    policy_hash: str = "sha256:policy-hash-001",
    subject_id: str = "RECOVERY-001",
    bound_at: datetime = BOUND_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> PolicyVersionBinding:
    return PolicyVersionBinding(
        binding_id=binding_id,
        policy_id=policy_id,
        policy_version=policy_version,
        policy_hash=policy_hash,
        subject_id=subject_id,
        bound_at=bound_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_policy_binding() -> None:
    policy = make_policy()
    binding = make_binding()

    assert (
        PolicyVersionBindingValidator().validate(
            binding,
            policy,
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )
        is True
    )


def test_validator_accepts_binding_created_before_reference_time() -> None:
    policy = make_policy()
    binding = make_binding(
        bound_at=BOUND_AT - timedelta(seconds=1),
    )

    assert (
        PolicyVersionBindingValidator().validate(
            binding,
            policy,
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )
        is True
    )


def test_validator_rejects_non_binding_input() -> None:
    with pytest.raises(
        TypeError,
        match="PolicyVersionBinding",
    ):
        PolicyVersionBindingValidator().validate(
            "PVB-001",  # type: ignore[arg-type]
            make_policy(),
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )


def test_validator_rejects_non_policy_input() -> None:
    with pytest.raises(
        TypeError,
        match="QuorumPolicy",
    ):
        PolicyVersionBindingValidator().validate(
            make_binding(),
            "QP-001",  # type: ignore[arg-type]
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )


def test_validator_rejects_policy_identity_mismatch() -> None:
    binding = make_binding(policy_id="QP-001")
    policy = make_policy(policy_id="QP-002")

    with pytest.raises(
        PolicyVersionBindingError,
        match="policy identity",
    ):
        PolicyVersionBindingValidator().validate(
            binding,
            policy,
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )


def test_validator_rejects_policy_version_mismatch() -> None:
    with pytest.raises(
        PolicyVersionBindingError,
        match="policy version",
    ):
        PolicyVersionBindingValidator().validate(
            make_binding(policy_version="1.0.0"),
            make_policy(),
            expected_policy_version="2.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )


def test_validator_rejects_policy_hash_mismatch() -> None:
    with pytest.raises(
        PolicyVersionBindingError,
        match="policy hash",
    ):
        PolicyVersionBindingValidator().validate(
            make_binding(
                policy_hash="sha256:policy-hash-001",
            ),
            make_policy(),
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-999",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )


def test_validator_rejects_subject_mismatch() -> None:
    with pytest.raises(
        PolicyVersionBindingError,
        match="subject",
    ):
        PolicyVersionBindingValidator().validate(
            make_binding(subject_id="RECOVERY-001"),
            make_policy(),
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-999",
            now=BOUND_AT,
        )


def test_validator_rejects_future_binding() -> None:
    with pytest.raises(
        PolicyVersionBindingError,
        match="future",
    ):
        PolicyVersionBindingValidator().validate(
            make_binding(
                bound_at=BOUND_AT + timedelta(seconds=1),
            ),
            make_policy(),
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=BOUND_AT,
        )


def test_binding_is_immutable() -> None:
    binding = make_binding()

    with pytest.raises((AttributeError, TypeError)):
        binding.policy_version = "2.0.0"  # type: ignore[misc]


def test_binding_rejects_empty_binding_id() -> None:
    with pytest.raises(ValueError, match="binding_id"):
        make_binding(binding_id="")


def test_binding_rejects_empty_policy_version() -> None:
    with pytest.raises(ValueError, match="policy_version"):
        make_binding(policy_version="")


def test_binding_rejects_empty_policy_hash() -> None:
    with pytest.raises(ValueError, match="policy_hash"):
        make_binding(policy_hash="")


def test_binding_rejects_naive_bound_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_binding(
            bound_at=datetime(2026, 7, 14, 12, 0),
        )


def test_validator_rejects_naive_reference_time() -> None:
    with pytest.raises(TypeError, match="timezone-aware"):
        PolicyVersionBindingValidator().validate(
            make_binding(),
            make_policy(),
            expected_policy_version="1.0.0",
            expected_policy_hash="sha256:policy-hash-001",
            subject_id="RECOVERY-001",
            now=datetime(2026, 7, 14, 12, 0),
        )


def test_binding_preserves_observer_only_boundary() -> None:
    binding = make_binding()

    assert binding.execution_requested is False
    assert binding.side_effects_permitted is False