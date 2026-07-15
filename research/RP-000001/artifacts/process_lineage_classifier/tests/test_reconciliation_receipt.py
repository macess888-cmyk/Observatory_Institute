from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import ReconciliationReceipt


ISSUED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_receipt(
    *,
    receipt_id: str = "RCP-001",
    recovery_status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    assessment_types: tuple[EventType, ...] = (
        EventType.AUTHORITY_CONVERGENCE,
        EventType.LINEAGE_RECONCILIATION,
        EventType.ROLLBACK_RECOVERY,
    ),
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
    applied_rules: tuple[str, ...] = ("RO-001",),
    reasons: tuple[str, ...] = (
        "All required recovery assessments passed.",
    ),
    missing_evidence: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
    issued_at: datetime = ISSUED_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    execution_requested: bool = False,
    side_effects_permitted: bool = False,
) -> ReconciliationReceipt:
    return ReconciliationReceipt(
        receipt_id=receipt_id,
        recovery_status=recovery_status,
        operational_status=operational_status,
        confidence=confidence,
        assessment_types=assessment_types,
        assessment_ids=assessment_ids,
        evidence_ids=evidence_ids,
        applied_rules=applied_rules,
        reasons=reasons,
        missing_evidence=missing_evidence,
        conflicts=conflicts,
        issued_at=issued_at,
        issuer_id=issuer_id,
        execution_requested=execution_requested,
        side_effects_permitted=side_effects_permitted,
    )


def test_receipt_accepts_verified_reconciliation() -> None:
    receipt = make_receipt()

    assert receipt.receipt_id == "RCP-001"
    assert (
        receipt.recovery_status
        is RecoveryDecisionStatus.RECOVERY_READY
    )
    assert receipt.operational_status is OperationalStatus.PASS
    assert receipt.confidence is ConfidenceLevel.HIGH
    assert len(receipt.assessment_types) == 3
    assert len(receipt.assessment_ids) == 3
    assert receipt.missing_evidence == ()
    assert receipt.conflicts == ()
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_receipt_accepts_held_reconciliation() -> None:
    receipt = make_receipt(
        recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        missing_evidence=("quorum confirmation evidence",),
        conflicts=("Authority convergence remains unresolved.",),
        applied_rules=("RO-002",),
    )

    assert (
        receipt.recovery_status
        is RecoveryDecisionStatus.RECOVERY_HOLD
    )
    assert receipt.operational_status is OperationalStatus.HOLD
    assert receipt.confidence is ConfidenceLevel.LOW
    assert receipt.missing_evidence
    assert receipt.conflicts


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises(
        (AttributeError, TypeError),
    ):
        receipt.receipt_id = "RCP-002"  # type: ignore[misc]


def test_receipt_rejects_empty_receipt_id() -> None:
    with pytest.raises(ValueError, match="receipt_id"):
        make_receipt(receipt_id="")


def test_receipt_rejects_empty_issuer_id() -> None:
    with pytest.raises(ValueError, match="issuer_id"):
        make_receipt(issuer_id="")


def test_receipt_rejects_naive_issued_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_receipt(
            issued_at=datetime(2026, 7, 14, 12, 0),
        )


def test_receipt_rejects_duplicate_assessment_types() -> None:
    with pytest.raises(ValueError, match="assessment_types"):
        make_receipt(
            assessment_types=(
                EventType.AUTHORITY_CONVERGENCE,
                EventType.AUTHORITY_CONVERGENCE,
                EventType.ROLLBACK_RECOVERY,
            ),
        )


def test_receipt_rejects_duplicate_assessment_ids() -> None:
    with pytest.raises(ValueError, match="assessment_ids"):
        make_receipt(
            assessment_ids=(
                "AUTHORITY-CONVERGENCE:001",
                "AUTHORITY-CONVERGENCE:001",
                "ROLLBACK-RECOVERY:001",
            ),
        )


def test_receipt_rejects_mismatched_assessment_counts() -> None:
    with pytest.raises(ValueError, match="assessment"):
        make_receipt(
            assessment_ids=(
                "AUTHORITY-CONVERGENCE:001",
                "LINEAGE-RECONCILIATION:001",
            ),
        )


def test_receipt_rejects_duplicate_evidence_ids() -> None:
    with pytest.raises(ValueError, match="evidence_ids"):
        make_receipt(
            evidence_ids=(
                "EVD-QUORUM-001",
                "EVD-QUORUM-001",
            ),
        )


def test_receipt_rejects_ready_status_with_hold_operational_status() -> None:
    with pytest.raises(ValueError, match="RECOVERY_READY"):
        make_receipt(
            recovery_status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.HOLD,
        )


def test_receipt_rejects_hold_status_with_pass_operational_status() -> None:
    with pytest.raises(ValueError, match="RECOVERY_HOLD"):
        make_receipt(
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.PASS,
        )


def test_receipt_rejects_ready_status_with_missing_evidence() -> None:
    with pytest.raises(ValueError, match="missing evidence"):
        make_receipt(
            missing_evidence=("quorum confirmation evidence",),
        )


def test_receipt_rejects_ready_status_with_conflicts() -> None:
    with pytest.raises(ValueError, match="conflicts"):
        make_receipt(
            conflicts=("Authority conflict remains.",),
        )


def test_receipt_rejects_execution_request() -> None:
    with pytest.raises(ValueError, match="observer-only"):
        make_receipt(execution_requested=True)


def test_receipt_rejects_side_effect_permission() -> None:
    with pytest.raises(ValueError, match="side effects"):
        make_receipt(side_effects_permitted=True)


def test_receipt_requires_event_type_members() -> None:
    with pytest.raises(TypeError, match="EventType"):
        make_receipt(
            assessment_types=(
                EventType.AUTHORITY_CONVERGENCE,
                "LINEAGE_RECONCILIATION",  # type: ignore[arg-type]
                EventType.ROLLBACK_RECOVERY,
            ),
        )


def test_receipt_requires_string_assessment_ids() -> None:
    with pytest.raises(TypeError, match="assessment_ids"):
        make_receipt(
            assessment_ids=(
                "AUTHORITY-CONVERGENCE:001",
                2,  # type: ignore[arg-type]
                "ROLLBACK-RECOVERY:001",
            ),
        )