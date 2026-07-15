from datetime import datetime, timezone

import pytest

from models import RecoveryIntegrityBundle
from services.recovery_integrity_bundle_validator import (
    RecoveryIntegrityBundleError,
    RecoveryIntegrityBundleValidator,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

RECONCILIATION_RECEIPT_DIGEST = "sha256:" + ("1" * 64)
AUDIT_ROOT_DIGEST = "sha256:" + ("2" * 64)
REPLAY_MANIFEST_DIGEST = "sha256:" + ("3" * 64)
VERIFICATION_RECEIPT_DIGEST = "sha256:" + ("4" * 64)
POLICY_DIGEST = "sha256:" + ("5" * 64)
TRUST_DIGEST_001 = "sha256:" + ("6" * 64)
TRUST_DIGEST_002 = "sha256:" + ("7" * 64)


def make_bundle(
    *,
    bundle_id: str = "RIB-001",
    subject_id: str = "RECOVERY-001",
    original_decision_id: str = "RD-001",
    reconciliation_receipt_id: str = "RCP-001",
    reconciliation_receipt_digest: str = (
        RECONCILIATION_RECEIPT_DIGEST
    ),
    audit_chain_id: str = "AHC-001",
    audit_root_digest: str = AUDIT_ROOT_DIGEST,
    replay_manifest_id: str = "RIM-001",
    replay_manifest_digest: str = REPLAY_MANIFEST_DIGEST,
    verification_receipt_id: str = "RVR-001",
    verification_receipt_digest: str = (
        VERIFICATION_RECEIPT_DIGEST
    ),
    policy_binding_id: str = "PVB-001",
    policy_digest: str = POLICY_DIGEST,
    trust_provenance_ids: tuple[str, ...] = (
        "TSP-001",
        "TSP-002",
    ),
    trust_digests: tuple[str, ...] = (
        TRUST_DIGEST_001,
        TRUST_DIGEST_002,
    ),
    created_at: datetime = CREATED_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> RecoveryIntegrityBundle:
    return RecoveryIntegrityBundle(
        bundle_id=bundle_id,
        subject_id=subject_id,
        original_decision_id=original_decision_id,
        reconciliation_receipt_id=reconciliation_receipt_id,
        reconciliation_receipt_digest=(
            reconciliation_receipt_digest
        ),
        audit_chain_id=audit_chain_id,
        audit_root_digest=audit_root_digest,
        replay_manifest_id=replay_manifest_id,
        replay_manifest_digest=replay_manifest_digest,
        verification_receipt_id=verification_receipt_id,
        verification_receipt_digest=(
            verification_receipt_digest
        ),
        policy_binding_id=policy_binding_id,
        policy_digest=policy_digest,
        trust_provenance_ids=trust_provenance_ids,
        trust_digests=trust_digests,
        created_at=created_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_integrity_bundle() -> None:
    bundle = make_bundle()

    assert RecoveryIntegrityBundleValidator().validate(bundle) is True


def test_bundle_is_immutable() -> None:
    bundle = make_bundle()

    with pytest.raises((AttributeError, TypeError)):
        bundle.audit_root_digest = POLICY_DIGEST  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "bundle_id",
        "subject_id",
        "original_decision_id",
        "reconciliation_receipt_id",
        "audit_chain_id",
        "replay_manifest_id",
        "verification_receipt_id",
        "policy_binding_id",
        "issuer_id",
    ],
)
def test_bundle_rejects_empty_identity(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_bundle(**{field_name: ""})


@pytest.mark.parametrize(
    "field_name",
    [
        "reconciliation_receipt_digest",
        "audit_root_digest",
        "replay_manifest_digest",
        "verification_receipt_digest",
        "policy_digest",
    ],
)
@pytest.mark.parametrize(
    "invalid_digest",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
    ],
)
def test_bundle_rejects_invalid_digest(
    field_name: str,
    invalid_digest: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_bundle(**{field_name: invalid_digest})


def test_bundle_rejects_empty_trust_provenance_ids() -> None:
    with pytest.raises(
        ValueError,
        match="trust_provenance_ids",
    ):
        make_bundle(
            trust_provenance_ids=(),
            trust_digests=(),
        )


def test_bundle_rejects_empty_trust_digests() -> None:
    with pytest.raises(
        ValueError,
        match="trust_digests",
    ):
        make_bundle(
            trust_provenance_ids=("TSP-001",),
            trust_digests=(),
        )


def test_bundle_rejects_mismatched_trust_counts() -> None:
    with pytest.raises(
        ValueError,
        match="matching counts",
    ):
        make_bundle(
            trust_provenance_ids=(
                "TSP-001",
                "TSP-002",
            ),
            trust_digests=(TRUST_DIGEST_001,),
        )


def test_bundle_rejects_duplicate_trust_provenance_ids() -> None:
    with pytest.raises(
        ValueError,
        match="duplicate trust provenance",
    ):
        make_bundle(
            trust_provenance_ids=(
                "TSP-001",
                "TSP-001",
            )
        )


def test_bundle_rejects_duplicate_trust_digests() -> None:
    with pytest.raises(
        ValueError,
        match="duplicate trust digest",
    ):
        make_bundle(
            trust_digests=(
                TRUST_DIGEST_001,
                TRUST_DIGEST_001,
            )
        )


def test_bundle_rejects_invalid_trust_digest() -> None:
    with pytest.raises(
        ValueError,
        match="trust_digests",
    ):
        make_bundle(
            trust_digests=(
                TRUST_DIGEST_001,
                "sha256:abc",
            )
        )


def test_bundle_rejects_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        make_bundle(
            created_at=datetime(2026, 7, 15, 12, 0),
        )


def test_validator_rejects_non_bundle_input() -> None:
    with pytest.raises(
        TypeError,
        match="RecoveryIntegrityBundle",
    ):
        RecoveryIntegrityBundleValidator().validate(
            "RIB-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    bundle = make_bundle()

    assert (
        RecoveryIntegrityBundleValidator().validate(
            bundle,
            expected_subject_id="RECOVERY-001",
            expected_decision_id="RD-001",
            expected_reconciliation_receipt_id="RCP-001",
            expected_reconciliation_receipt_digest=(
                RECONCILIATION_RECEIPT_DIGEST
            ),
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_replay_manifest_id="RIM-001",
            expected_replay_manifest_digest=(
                REPLAY_MANIFEST_DIGEST
            ),
            expected_verification_receipt_id="RVR-001",
            expected_verification_receipt_digest=(
                VERIFICATION_RECEIPT_DIGEST
            ),
            expected_policy_binding_id="PVB-001",
            expected_policy_digest=POLICY_DIGEST,
        )
        is True
    )


@pytest.mark.parametrize(
    (
        "expected_field",
        "expected_value",
        "error_match",
    ),
    [
        (
            "expected_subject_id",
            "RECOVERY-999",
            "subject identity",
        ),
        (
            "expected_decision_id",
            "RD-999",
            "decision identity",
        ),
        (
            "expected_reconciliation_receipt_id",
            "RCP-999",
            "reconciliation receipt identity",
        ),
        (
            "expected_reconciliation_receipt_digest",
            "sha256:" + ("8" * 64),
            "reconciliation receipt digest",
        ),
        (
            "expected_audit_chain_id",
            "AHC-999",
            "audit chain identity",
        ),
        (
            "expected_audit_root_digest",
            "sha256:" + ("8" * 64),
            "audit root digest",
        ),
        (
            "expected_replay_manifest_id",
            "RIM-999",
            "replay manifest identity",
        ),
        (
            "expected_replay_manifest_digest",
            "sha256:" + ("8" * 64),
            "replay manifest digest",
        ),
        (
            "expected_verification_receipt_id",
            "RVR-999",
            "verification receipt identity",
        ),
        (
            "expected_verification_receipt_digest",
            "sha256:" + ("8" * 64),
            "verification receipt digest",
        ),
        (
            "expected_policy_binding_id",
            "PVB-999",
            "policy binding identity",
        ),
        (
            "expected_policy_digest",
            "sha256:" + ("8" * 64),
            "policy digest",
        ),
    ],
)
def test_validator_rejects_reference_mismatch(
    expected_field: str,
    expected_value: str,
    error_match: str,
) -> None:
    arguments = {
        "expected_subject_id": "RECOVERY-001",
        "expected_decision_id": "RD-001",
        "expected_reconciliation_receipt_id": "RCP-001",
        "expected_reconciliation_receipt_digest": (
            RECONCILIATION_RECEIPT_DIGEST
        ),
        "expected_audit_chain_id": "AHC-001",
        "expected_audit_root_digest": AUDIT_ROOT_DIGEST,
        "expected_replay_manifest_id": "RIM-001",
        "expected_replay_manifest_digest": (
            REPLAY_MANIFEST_DIGEST
        ),
        "expected_verification_receipt_id": "RVR-001",
        "expected_verification_receipt_digest": (
            VERIFICATION_RECEIPT_DIGEST
        ),
        "expected_policy_binding_id": "PVB-001",
        "expected_policy_digest": POLICY_DIGEST,
    }
    arguments[expected_field] = expected_value

    with pytest.raises(
        RecoveryIntegrityBundleError,
        match=error_match,
    ):
        RecoveryIntegrityBundleValidator().validate(
            make_bundle(),
            **arguments,
        )


def test_validator_does_not_mutate_bundle() -> None:
    bundle = make_bundle()
    original = bundle

    RecoveryIntegrityBundleValidator().validate(bundle)

    assert bundle == original


def test_bundle_preserves_observer_only_boundary() -> None:
    bundle = make_bundle()

    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False