from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import ReconciliationReceipt
from services.reconciliation_receipt_hasher import (
    ReconciliationReceiptHashingError,
    ReconciliationReceiptHasher,
)


ISSUED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


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
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_returns_sha256_digest() -> None:
    result = ReconciliationReceiptHasher().hash(make_receipt())

    assert result.algorithm == "sha256"
    assert result.digest.startswith("sha256:")
    assert len(result.digest.removeprefix("sha256:")) == 64
    assert result.receipt_id == "RCP-001"
    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_hasher_is_deterministic() -> None:
    receipt = make_receipt()

    first = ReconciliationReceiptHasher().hash(receipt)
    second = ReconciliationReceiptHasher().hash(receipt)

    assert first == second
    assert first.digest == second.digest
    assert first.canonical_payload == second.canonical_payload


def test_hasher_produces_same_digest_for_equivalent_receipts() -> None:
    first = make_receipt()
    second = make_receipt()

    assert (
        ReconciliationReceiptHasher().hash(first).digest
        == ReconciliationReceiptHasher().hash(second).digest
    )


def test_hasher_preserves_canonical_field_order() -> None:
    result = ReconciliationReceiptHasher().hash(make_receipt())

    expected_keys = (
        "receipt_id",
        "recovery_status",
        "operational_status",
        "confidence",
        "assessment_types",
        "assessment_ids",
        "evidence_ids",
        "applied_rules",
        "reasons",
        "missing_evidence",
        "conflicts",
        "issued_at",
        "issuer_id",
        "execution_requested",
        "side_effects_permitted",
    )

    positions = tuple(
        result.canonical_payload.index(f'"{key}"')
        for key in expected_keys
    )

    assert positions == tuple(sorted(positions))


def test_hasher_serializes_enum_values() -> None:
    result = ReconciliationReceiptHasher().hash(make_receipt())

    assert '"recovery_status":"RECOVERY_READY"' in result.canonical_payload
    assert '"operational_status":"PASS"' in result.canonical_payload
    assert '"confidence":"HIGH"' in result.canonical_payload
    assert '"AUTHORITY_CONVERGENCE"' in result.canonical_payload


def test_hasher_serializes_timestamp_in_iso_format() -> None:
    result = ReconciliationReceiptHasher().hash(make_receipt())

    assert ISSUED_AT.isoformat() in result.canonical_payload


def test_hasher_is_sensitive_to_receipt_identity() -> None:
    first = ReconciliationReceiptHasher().hash(
        make_receipt(receipt_id="RCP-001")
    )
    second = ReconciliationReceiptHasher().hash(
        make_receipt(receipt_id="RCP-002")
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_recovery_status() -> None:
    ready = ReconciliationReceiptHasher().hash(make_receipt())
    held = ReconciliationReceiptHasher().hash(
        make_receipt(
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            missing_evidence=("quorum evidence",),
            applied_rules=("RO-002",),
        )
    )

    assert ready.digest != held.digest


def test_hasher_is_sensitive_to_assessment_references() -> None:
    first = ReconciliationReceiptHasher().hash(make_receipt())
    second = ReconciliationReceiptHasher().hash(
        make_receipt(
            assessment_ids=(
                "AUTHORITY-CONVERGENCE:002",
                "LINEAGE-RECONCILIATION:001",
                "ROLLBACK-RECOVERY:001",
            )
        )
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_evidence_references() -> None:
    first = ReconciliationReceiptHasher().hash(make_receipt())
    second = ReconciliationReceiptHasher().hash(
        make_receipt(
            evidence_ids=(
                "EVD-QUORUM-999",
                "EVD-LINEAGE-001",
                "EVD-INTEGRITY-001",
            )
        )
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_rules() -> None:
    first = ReconciliationReceiptHasher().hash(
        make_receipt(applied_rules=("RO-001",))
    )
    second = ReconciliationReceiptHasher().hash(
        make_receipt(applied_rules=("RO-999",))
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_reasons() -> None:
    first = ReconciliationReceiptHasher().hash(
        make_receipt(reasons=("Recovery readiness established.",))
    )
    second = ReconciliationReceiptHasher().hash(
        make_receipt(reasons=("Different explanation.",))
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_issue_time() -> None:
    first = ReconciliationReceiptHasher().hash(make_receipt())
    second = ReconciliationReceiptHasher().hash(
        make_receipt(
            issued_at=datetime(
                2026,
                7,
                15,
                12,
                0,
                1,
                tzinfo=timezone.utc,
            )
        )
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_issuer_identity() -> None:
    first = ReconciliationReceiptHasher().hash(
        make_receipt(issuer_id="PROCESS-LINEAGE-CLASSIFIER")
    )
    second = ReconciliationReceiptHasher().hash(
        make_receipt(issuer_id="OTHER-ISSUER")
    )

    assert first.digest != second.digest


def test_hasher_rejects_non_receipt_input() -> None:
    with pytest.raises(TypeError, match="ReconciliationReceipt"):
        ReconciliationReceiptHasher().hash(
            "RCP-001"  # type: ignore[arg-type]
        )


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    ReconciliationReceiptHasher().hash(receipt)

    assert receipt == original


def test_hasher_preserves_observer_only_boundary() -> None:
    result = ReconciliationReceiptHasher().hash(make_receipt())

    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_hash_result_is_immutable() -> None:
    result = ReconciliationReceiptHasher().hash(make_receipt())

    with pytest.raises((AttributeError, TypeError)):
        result.digest = "sha256:changed"  # type: ignore[misc]


def test_hash_result_rejects_invalid_algorithm() -> None:
    from models import ReconciliationReceiptHash

    with pytest.raises(
        ReconciliationReceiptHashingError,
        match="algorithm",
    ):
        ReconciliationReceiptHash(
            receipt_id="RCP-001",
            algorithm="md5",
            digest="md5:invalid",
            canonical_payload="{}",
            execution_requested=False,
            side_effects_permitted=False,
        )
