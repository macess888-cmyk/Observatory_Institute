from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import (
    ReconciliationReceipt,
    RecoveryDecision,
)
from services.reconciliation_receipt_service import (
    ReconciliationReceiptGenerationError,
    ReconciliationReceiptService,
)


ISSUED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_decision(
    *,
    status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    missing_assessment_types: tuple[EventType, ...] = (),
    missing_evidence: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
    applied_rules: tuple[str, ...] = ("RO-001",),
) -> RecoveryDecision:
    return RecoveryDecision(
        status=status,
        operational_status=operational_status,
        confidence=confidence,
        required_assessments=3,
        passed_assessments=(
            3
            if status is RecoveryDecisionStatus.RECOVERY_READY
            else 2
        ),
        held_assessments=(
            0
            if status is RecoveryDecisionStatus.RECOVERY_READY
            else 1
        ),
        missing_assessment_types=missing_assessment_types,
        applied_rules=applied_rules,
        reasons=("Recovery decision recorded.",),
        missing_evidence=missing_evidence,
        conflicts=conflicts,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_assessment_types() -> tuple[EventType, ...]:
    return (
        EventType.AUTHORITY_CONVERGENCE,
        EventType.LINEAGE_RECONCILIATION,
        EventType.ROLLBACK_RECOVERY,
    )


def make_assessment_ids() -> tuple[str, ...]:
    return (
        "AUTHORITY-CONVERGENCE:001",
        "LINEAGE-RECONCILIATION:001",
        "ROLLBACK-RECOVERY:001",
    )


def make_evidence_ids() -> tuple[str, ...]:
    return (
        "EVD-QUORUM-001",
        "EVD-LINEAGE-001",
        "EVD-INTEGRITY-001",
    )


def test_service_generates_ready_receipt() -> None:
    decision = make_decision()

    receipt = ReconciliationReceiptService().generate(
        receipt_id="RCP-001",
        decision=decision,
        assessment_types=make_assessment_types(),
        assessment_ids=make_assessment_ids(),
        evidence_ids=make_evidence_ids(),
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert isinstance(receipt, ReconciliationReceipt)
    assert receipt.receipt_id == "RCP-001"
    assert (
        receipt.recovery_status
        is RecoveryDecisionStatus.RECOVERY_READY
    )
    assert receipt.operational_status is OperationalStatus.PASS
    assert receipt.confidence is ConfidenceLevel.HIGH
    assert receipt.assessment_types == make_assessment_types()
    assert receipt.assessment_ids == make_assessment_ids()
    assert receipt.evidence_ids == make_evidence_ids()
    assert receipt.applied_rules == ("RO-001",)
    assert receipt.missing_evidence == ()
    assert receipt.conflicts == ()
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_service_generates_held_receipt() -> None:
    decision = make_decision(
        status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        missing_evidence=("quorum confirmation evidence",),
        conflicts=("Authority convergence unresolved.",),
        applied_rules=("RO-002",),
    )

    receipt = ReconciliationReceiptService().generate(
        receipt_id="RCP-002",
        decision=decision,
        assessment_types=make_assessment_types(),
        assessment_ids=make_assessment_ids(),
        evidence_ids=make_evidence_ids(),
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert (
        receipt.recovery_status
        is RecoveryDecisionStatus.RECOVERY_HOLD
    )
    assert receipt.operational_status is OperationalStatus.HOLD
    assert receipt.confidence is ConfidenceLevel.LOW
    assert receipt.missing_evidence == (
        "quorum confirmation evidence",
    )
    assert receipt.conflicts == (
        "Authority convergence unresolved.",
    )
    assert receipt.applied_rules == ("RO-002",)


def test_service_preserves_decision_reasons() -> None:
    decision = make_decision()

    receipt = ReconciliationReceiptService().generate(
        receipt_id="RCP-001",
        decision=decision,
        assessment_types=make_assessment_types(),
        assessment_ids=make_assessment_ids(),
        evidence_ids=make_evidence_ids(),
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert receipt.reasons == decision.reasons


def test_service_rejects_missing_assessment_types() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="assessment types",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=(),
            assessment_ids=(),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_missing_assessment_ids() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="assessment identities",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=make_assessment_types(),
            assessment_ids=(),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_missing_evidence_ids() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="evidence",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=make_assessment_types(),
            assessment_ids=make_assessment_ids(),
            evidence_ids=(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_mismatched_assessment_counts() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="matching",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=make_assessment_types(),
            assessment_ids=(
                "AUTHORITY-CONVERGENCE:001",
                "LINEAGE-RECONCILIATION:001",
            ),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_assessment_types() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="duplicate assessment type",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=(
                EventType.AUTHORITY_CONVERGENCE,
                EventType.AUTHORITY_CONVERGENCE,
                EventType.ROLLBACK_RECOVERY,
            ),
            assessment_ids=make_assessment_ids(),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_assessment_ids() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="duplicate assessment identity",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=make_assessment_types(),
            assessment_ids=(
                "AUTHORITY-CONVERGENCE:001",
                "AUTHORITY-CONVERGENCE:001",
                "ROLLBACK-RECOVERY:001",
            ),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_evidence_ids() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="duplicate evidence",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=make_assessment_types(),
            assessment_ids=make_assessment_ids(),
            evidence_ids=(
                "EVD-QUORUM-001",
                "EVD-QUORUM-001",
            ),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_missing_required_ready_assessment() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="required assessment",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=(
                EventType.AUTHORITY_CONVERGENCE,
                EventType.LINEAGE_RECONCILIATION,
                EventType.SPLIT_BRAIN_RECOVERY,
            ),
            assessment_ids=make_assessment_ids(),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_non_recovery_decision() -> None:
    with pytest.raises(TypeError, match="RecoveryDecision"):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision="RECOVERY_READY",  # type: ignore[arg-type]
            assessment_types=make_assessment_types(),
            assessment_ids=make_assessment_ids(),
            evidence_ids=make_evidence_ids(),
            issued_at=ISSUED_AT,
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_naive_issue_time() -> None:
    decision = make_decision()

    with pytest.raises(
        ReconciliationReceiptGenerationError,
        match="timezone-aware",
    ):
        ReconciliationReceiptService().generate(
            receipt_id="RCP-001",
            decision=decision,
            assessment_types=make_assessment_types(),
            assessment_ids=make_assessment_ids(),
            evidence_ids=make_evidence_ids(),
            issued_at=datetime(2026, 7, 14, 12, 0),
            issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_does_not_mutate_decision() -> None:
    decision = make_decision()
    original = decision

    ReconciliationReceiptService().generate(
        receipt_id="RCP-001",
        decision=decision,
        assessment_types=make_assessment_types(),
        assessment_ids=make_assessment_ids(),
        evidence_ids=make_evidence_ids(),
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert decision == original


def test_service_preserves_observer_only_boundary() -> None:
    receipt = ReconciliationReceiptService().generate(
        receipt_id="RCP-001",
        decision=make_decision(),
        assessment_types=make_assessment_types(),
        assessment_ids=make_assessment_ids(),
        evidence_ids=make_evidence_ids(),
        issued_at=ISSUED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False