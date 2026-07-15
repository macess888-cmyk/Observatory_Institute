from datetime import datetime, timezone

import pytest

from models import (
    RecoveryDecisionVerification,
    RecoveryVerificationReceipt,
)
from services.recovery_verification_receipt_service import (
    RecoveryVerificationReceiptError,
    RecoveryVerificationReceiptService,
)


ISSUED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

REPLAY_MANIFEST_DIGEST = "sha256:" + ("1" * 64)
AUDIT_ROOT_DIGEST = "sha256:" + ("2" * 64)
DECISION_DIGEST = "sha256:" + ("3" * 64)


def make_verification(
    *,
    verification_id: str = "RDV-001",
    replay_id: str = "RDR-001",
    original_decision_id: str = "RD-001",
) -> RecoveryDecisionVerification:
    return RecoveryDecisionVerification(
        verification_id=verification_id,
        replay_id=replay_id,
        original_decision_id=original_decision_id,
        verified=True,
        replay_verified=True,
        status_match=True,
        operational_status_match=True,
        confidence_match=True,
        rules_match=True,
        reasons_match=True,
        missing_evidence_match=True,
        conflicts_match=True,
        verified_at=ISSUED_AT,
        verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_generates_verification_receipt() -> None:
    verification = make_verification()

    receipt = RecoveryVerificationReceiptService().generate(
        receipt_id="RVR-001",
        verification=verification,
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        decision_digest=DECISION_DIGEST,
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert isinstance(receipt, RecoveryVerificationReceipt)
    assert receipt.receipt_id == "RVR-001"
    assert receipt.verification_id == "RDV-001"
    assert receipt.replay_id == "RDR-001"
    assert receipt.original_decision_id == "RD-001"
    assert receipt.replay_manifest_id == "RIM-001"
    assert receipt.replay_manifest_digest == REPLAY_MANIFEST_DIGEST
    assert receipt.audit_chain_id == "AHC-001"
    assert receipt.audit_root_digest == AUDIT_ROOT_DIGEST
    assert receipt.decision_digest == DECISION_DIGEST
    assert receipt.verified is True
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_service_preserves_verification_identity() -> None:
    verification = make_verification(
        verification_id="RDV-999",
        replay_id="RDR-999",
        original_decision_id="RD-999",
    )

    receipt = RecoveryVerificationReceiptService().generate(
        receipt_id="RVR-001",
        verification=verification,
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        decision_digest=DECISION_DIGEST,
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert receipt.verification_id == "RDV-999"
    assert receipt.replay_id == "RDR-999"
    assert receipt.original_decision_id == "RD-999"


def test_service_rejects_unverified_verification() -> None:
    verification = RecoveryDecisionVerification(
        verification_id="RDV-001",
        replay_id="RDR-001",
        original_decision_id="RD-001",
        verified=False,
        replay_verified=False,
        status_match=False,
        operational_status_match=False,
        confidence_match=False,
        rules_match=False,
        reasons_match=False,
        missing_evidence_match=False,
        conflicts_match=False,
        verified_at=ISSUED_AT,
        verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )

    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="verified",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification=verification,
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_verification_input() -> None:
    with pytest.raises(
        TypeError,
        match="RecoveryDecisionVerification",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification="RDV-001",  # type: ignore[arg-type]
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_receipt_id() -> None:
    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="receipt_id",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="",
            verification=make_verification(),
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_manifest_id() -> None:
    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="replay_manifest_id",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification=make_verification(),
            replay_manifest_id="",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_audit_chain_id() -> None:
    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="audit_chain_id",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification=make_verification(),
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_issuer_id() -> None:
    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="issuer_id",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification=make_verification(),
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=ISSUED_AT,
            issuer_id="",
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("replay_manifest_digest", "md5:invalid"),
        ("audit_root_digest", "md5:invalid"),
        ("decision_digest", "md5:invalid"),
        ("replay_manifest_digest", "sha256:abc"),
        ("audit_root_digest", "sha256:abc"),
        ("decision_digest", "sha256:abc"),
        ("replay_manifest_digest", "sha256:" + ("z" * 64)),
        ("audit_root_digest", "sha256:" + ("z" * 64)),
        ("decision_digest", "sha256:" + ("z" * 64)),
    ],
)
def test_service_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "receipt_id": "RVR-001",
        "verification": make_verification(),
        "replay_manifest_id": "RIM-001",
        "replay_manifest_digest": REPLAY_MANIFEST_DIGEST,
        "audit_chain_id": "AHC-001",
        "audit_root_digest": AUDIT_ROOT_DIGEST,
        "decision_digest": DECISION_DIGEST,
        "issued_at": ISSUED_AT,
        "issuer_id": "PROCESS-LINEAGE-CLASSIFIER",
    }
    arguments[field_name] = value

    with pytest.raises(
        RecoveryVerificationReceiptError,
        match=field_name,
    ):
        RecoveryVerificationReceiptService().generate(**arguments)


def test_service_rejects_naive_issue_time() -> None:
    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="timezone-aware",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification=make_verification(),
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=datetime(2026, 7, 15, 12, 0),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_issue_before_verification() -> None:
    verification = make_verification()

    with pytest.raises(
        RecoveryVerificationReceiptError,
        match="before verification",
    ):
        RecoveryVerificationReceiptService().generate(
            receipt_id="RVR-001",
            verification=verification,
            replay_manifest_id="RIM-001",
            replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
            audit_chain_id="AHC-001",
            audit_root_digest=AUDIT_ROOT_DIGEST,
            decision_digest=DECISION_DIGEST,
            issued_at=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            ),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_receipt_is_immutable() -> None:
    receipt = RecoveryVerificationReceiptService().generate(
        receipt_id="RVR-001",
        verification=make_verification(),
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        decision_digest=DECISION_DIGEST,
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    with pytest.raises((AttributeError, TypeError)):
        receipt.verified = False  # type: ignore[misc]


def test_service_does_not_mutate_verification() -> None:
    verification = make_verification()
    original = verification

    RecoveryVerificationReceiptService().generate(
        receipt_id="RVR-001",
        verification=verification,
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        decision_digest=DECISION_DIGEST,
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert verification == original


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = RecoveryVerificationReceiptService().generate(
        receipt_id="RVR-001",
        verification=make_verification(),
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        decision_digest=DECISION_DIGEST,
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False