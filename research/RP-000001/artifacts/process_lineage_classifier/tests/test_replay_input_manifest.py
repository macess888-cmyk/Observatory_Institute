from datetime import datetime, timezone

import pytest

from models import ReplayInputManifest
from services.replay_input_manifest_validator import (
    ReplayInputManifestError,
    ReplayInputManifestValidator,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

RECEIPT_DIGEST = "sha256:" + ("1" * 64)
AUDIT_ROOT_DIGEST = "sha256:" + ("2" * 64)
POLICY_DIGEST = "sha256:" + ("3" * 64)
TRUST_DIGEST = "sha256:" + ("4" * 64)


def make_manifest(
    *,
    manifest_id: str = "RIM-001",
    original_decision_id: str = "RD-001",
    assessment_ids: tuple[str, ...] = (
        "AUTHORITY-CONVERGENCE:001",
        "LINEAGE-RECONCILIATION:001",
        "ROLLBACK-RECOVERY:001",
    ),
    evidence_ids: tuple[str, ...] = (
        "EVD-QUORUM-001",
        "EVD-LINEAGE-001",
        "EVD-INTEGRITY-001",
    ),
    receipt_id: str = "RCP-001",
    receipt_digest: str = RECEIPT_DIGEST,
    audit_chain_id: str = "AHC-001",
    audit_root_digest: str = AUDIT_ROOT_DIGEST,
    policy_binding_id: str = "PVB-001",
    policy_digest: str = POLICY_DIGEST,
    trust_provenance_ids: tuple[str, ...] = (
        "TSP-001",
        "TSP-002",
    ),
    trust_digests: tuple[str, ...] = (
        TRUST_DIGEST,
        "sha256:" + ("5" * 64),
    ),
    created_at: datetime = CREATED_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> ReplayInputManifest:
    return ReplayInputManifest(
        manifest_id=manifest_id,
        original_decision_id=original_decision_id,
        assessment_ids=assessment_ids,
        evidence_ids=evidence_ids,
        receipt_id=receipt_id,
        receipt_digest=receipt_digest,
        audit_chain_id=audit_chain_id,
        audit_root_digest=audit_root_digest,
        policy_binding_id=policy_binding_id,
        policy_digest=policy_digest,
        trust_provenance_ids=trust_provenance_ids,
        trust_digests=trust_digests,
        created_at=created_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_manifest() -> None:
    manifest = make_manifest()

    assert ReplayInputManifestValidator().validate(manifest) is True


def test_manifest_is_immutable() -> None:
    manifest = make_manifest()

    with pytest.raises((AttributeError, TypeError)):
        manifest.receipt_digest = AUDIT_ROOT_DIGEST  # type: ignore[misc]


def test_manifest_rejects_empty_manifest_id() -> None:
    with pytest.raises(ValueError, match="manifest_id"):
        make_manifest(manifest_id="")


def test_manifest_rejects_empty_original_decision_id() -> None:
    with pytest.raises(ValueError, match="original_decision_id"):
        make_manifest(original_decision_id="")


def test_manifest_rejects_empty_assessment_ids() -> None:
    with pytest.raises(ValueError, match="assessment_ids"):
        make_manifest(assessment_ids=())


def test_manifest_rejects_empty_evidence_ids() -> None:
    with pytest.raises(ValueError, match="evidence_ids"):
        make_manifest(evidence_ids=())


def test_manifest_rejects_duplicate_assessment_ids() -> None:
    with pytest.raises(ValueError, match="duplicate assessment"):
        make_manifest(
            assessment_ids=(
                "ASSESSMENT-001",
                "ASSESSMENT-001",
            )
        )


def test_manifest_rejects_duplicate_evidence_ids() -> None:
    with pytest.raises(ValueError, match="duplicate evidence"):
        make_manifest(
            evidence_ids=(
                "EVD-001",
                "EVD-001",
            )
        )


def test_manifest_rejects_empty_receipt_id() -> None:
    with pytest.raises(ValueError, match="receipt_id"):
        make_manifest(receipt_id="")


def test_manifest_rejects_empty_audit_chain_id() -> None:
    with pytest.raises(ValueError, match="audit_chain_id"):
        make_manifest(audit_chain_id="")


def test_manifest_rejects_empty_policy_binding_id() -> None:
    with pytest.raises(ValueError, match="policy_binding_id"):
        make_manifest(policy_binding_id="")


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("receipt_digest", "md5:invalid"),
        ("audit_root_digest", "md5:invalid"),
        ("policy_digest", "md5:invalid"),
        ("receipt_digest", "sha256:abc"),
        ("audit_root_digest", "sha256:abc"),
        ("policy_digest", "sha256:abc"),
        ("receipt_digest", "sha256:" + ("z" * 64)),
        ("audit_root_digest", "sha256:" + ("z" * 64)),
        ("policy_digest", "sha256:" + ("z" * 64)),
    ],
)
def test_manifest_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {field_name: value}

    with pytest.raises(ValueError, match=field_name):
        make_manifest(**arguments)


def test_manifest_rejects_empty_trust_provenance_ids() -> None:
    with pytest.raises(ValueError, match="trust_provenance_ids"):
        make_manifest(
            trust_provenance_ids=(),
            trust_digests=(),
        )


def test_manifest_rejects_empty_trust_digests() -> None:
    with pytest.raises(ValueError, match="trust_digests"):
        make_manifest(
            trust_provenance_ids=("TSP-001",),
            trust_digests=(),
        )


def test_manifest_rejects_mismatched_trust_reference_counts() -> None:
    with pytest.raises(ValueError, match="matching counts"):
        make_manifest(
            trust_provenance_ids=(
                "TSP-001",
                "TSP-002",
            ),
            trust_digests=(TRUST_DIGEST,),
        )


def test_manifest_rejects_duplicate_trust_provenance_ids() -> None:
    with pytest.raises(ValueError, match="duplicate trust provenance"):
        make_manifest(
            trust_provenance_ids=(
                "TSP-001",
                "TSP-001",
            ),
        )


def test_manifest_rejects_duplicate_trust_digests() -> None:
    with pytest.raises(ValueError, match="duplicate trust digest"):
        make_manifest(
            trust_digests=(
                TRUST_DIGEST,
                TRUST_DIGEST,
            ),
        )


def test_manifest_rejects_invalid_trust_digest() -> None:
    with pytest.raises(ValueError, match="trust_digests"):
        make_manifest(
            trust_digests=(
                TRUST_DIGEST,
                "sha256:abc",
            ),
        )


def test_manifest_rejects_naive_created_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_manifest(
            created_at=datetime(2026, 7, 15, 12, 0),
        )


def test_manifest_rejects_empty_issuer_id() -> None:
    with pytest.raises(ValueError, match="issuer_id"):
        make_manifest(issuer_id="")


def test_validator_rejects_non_manifest_input() -> None:
    with pytest.raises(TypeError, match="ReplayInputManifest"):
        ReplayInputManifestValidator().validate(
            "RIM-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_integrity_references() -> None:
    manifest = make_manifest()

    assert (
        ReplayInputManifestValidator().validate(
            manifest,
            expected_receipt_id="RCP-001",
            expected_receipt_digest=RECEIPT_DIGEST,
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_policy_binding_id="PVB-001",
            expected_policy_digest=POLICY_DIGEST,
        )
        is True
    )


def test_validator_rejects_receipt_identity_mismatch() -> None:
    with pytest.raises(
        ReplayInputManifestError,
        match="receipt identity",
    ):
        ReplayInputManifestValidator().validate(
            make_manifest(),
            expected_receipt_id="RCP-999",
            expected_receipt_digest=RECEIPT_DIGEST,
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_policy_binding_id="PVB-001",
            expected_policy_digest=POLICY_DIGEST,
        )


def test_validator_rejects_receipt_digest_mismatch() -> None:
    with pytest.raises(
        ReplayInputManifestError,
        match="receipt digest",
    ):
        ReplayInputManifestValidator().validate(
            make_manifest(),
            expected_receipt_id="RCP-001",
            expected_receipt_digest="sha256:" + ("9" * 64),
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_policy_binding_id="PVB-001",
            expected_policy_digest=POLICY_DIGEST,
        )


def test_validator_rejects_audit_chain_identity_mismatch() -> None:
    with pytest.raises(
        ReplayInputManifestError,
        match="audit chain identity",
    ):
        ReplayInputManifestValidator().validate(
            make_manifest(),
            expected_receipt_id="RCP-001",
            expected_receipt_digest=RECEIPT_DIGEST,
            expected_audit_chain_id="AHC-999",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_policy_binding_id="PVB-001",
            expected_policy_digest=POLICY_DIGEST,
        )


def test_validator_rejects_audit_root_digest_mismatch() -> None:
    with pytest.raises(
        ReplayInputManifestError,
        match="audit root digest",
    ):
        ReplayInputManifestValidator().validate(
            make_manifest(),
            expected_receipt_id="RCP-001",
            expected_receipt_digest=RECEIPT_DIGEST,
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest="sha256:" + ("8" * 64),
            expected_policy_binding_id="PVB-001",
            expected_policy_digest=POLICY_DIGEST,
        )


def test_validator_rejects_policy_binding_identity_mismatch() -> None:
    with pytest.raises(
        ReplayInputManifestError,
        match="policy binding identity",
    ):
        ReplayInputManifestValidator().validate(
            make_manifest(),
            expected_receipt_id="RCP-001",
            expected_receipt_digest=RECEIPT_DIGEST,
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_policy_binding_id="PVB-999",
            expected_policy_digest=POLICY_DIGEST,
        )


def test_validator_rejects_policy_digest_mismatch() -> None:
    with pytest.raises(
        ReplayInputManifestError,
        match="policy digest",
    ):
        ReplayInputManifestValidator().validate(
            make_manifest(),
            expected_receipt_id="RCP-001",
            expected_receipt_digest=RECEIPT_DIGEST,
            expected_audit_chain_id="AHC-001",
            expected_audit_root_digest=AUDIT_ROOT_DIGEST,
            expected_policy_binding_id="PVB-001",
            expected_policy_digest="sha256:" + ("7" * 64),
        )


def test_validator_does_not_mutate_manifest() -> None:
    manifest = make_manifest()
    original = manifest

    ReplayInputManifestValidator().validate(manifest)

    assert manifest == original


def test_manifest_preserves_observer_only_boundary() -> None:
    manifest = make_manifest()

    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False