import hashlib
import json

import pytest

from models.historical_admissibility_evidence_admission_receipt import (
    HistoricalAdmissibilityEvidenceAdmissionReceipt,
)
from services.historical_admissibility_evidence_admission_receipt_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptHasher,
)


def make_receipt(
    *,
    receipt_id: str = "HAEAR-000001",
    assessment_id: str = "HAEAA-000001",
    assessment_hash: str = "a" * 64,
    trust_receipt_id: str = "HAETR-000001",
    trust_receipt_hash: str = "b" * 64,
    admission_status: str = "HOLD",
    policy_version: str = "historical-evidence-admission-v1",
    recorded_at: str = "2026-07-16T21:30:00Z",
) -> HistoricalAdmissibilityEvidenceAdmissionReceipt:
    return HistoricalAdmissibilityEvidenceAdmissionReceipt(
        receipt_id=receipt_id,
        assessment_id=assessment_id,
        assessment_hash=assessment_hash,
        trust_receipt_id=trust_receipt_id,
        trust_receipt_hash=trust_receipt_hash,
        admission_status=admission_status,
        policy_version=policy_version,
        recorded_at=recorded_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    receipt: HistoricalAdmissibilityEvidenceAdmissionReceipt,
) -> str:
    payload = {
        "admission_status": receipt.admission_status,
        "assessment_hash": receipt.assessment_hash,
        "assessment_id": receipt.assessment_id,
        "authorization_granted": receipt.authorization_granted,
        "evidence_admitted": receipt.evidence_admitted,
        "execution_requested": receipt.execution_requested,
        "policy_version": receipt.policy_version,
        "receipt_id": receipt.receipt_id,
        "recorded_at": receipt.recorded_at,
        "side_effects_permitted": receipt.side_effects_permitted,
        "trust_receipt_hash": receipt.trust_receipt_hash,
        "trust_receipt_id": receipt.trust_receipt_id,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()

    result = hasher.hash_receipt(receipt)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()

    assert hasher.hash_receipt(receipt) == expected_hash(receipt)


def test_hasher_is_deterministic() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()

    assert hasher.hash_receipt(receipt) == hasher.hash_receipt(receipt)


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()

    assert hasher.hash_receipt(make_receipt()) == hasher.hash_receipt(
        make_receipt()
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("receipt_id", "HAEAR-000002"),
        ("assessment_id", "HAEAA-000002"),
        ("assessment_hash", "c" * 64),
        ("trust_receipt_id", "HAETR-000002"),
        ("trust_receipt_hash", "d" * 64),
        ("admission_status", "PASS"),
        ("policy_version", "historical-evidence-admission-v2"),
        ("recorded_at", "2026-07-16T21:31:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_receipt()

    values = {
        "receipt_id": baseline.receipt_id,
        "assessment_id": baseline.assessment_id,
        "assessment_hash": baseline.assessment_hash,
        "trust_receipt_id": baseline.trust_receipt_id,
        "trust_receipt_hash": baseline.trust_receipt_hash,
        "admission_status": baseline.admission_status,
        "policy_version": baseline.policy_version,
        "recorded_at": baseline.recorded_at,
    }
    values[field_name] = changed_value

    changed = make_receipt(**values)

    hasher = HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()

    assert hasher.hash_receipt(baseline) != hasher.hash_receipt(changed)


def test_hasher_rejects_none_receipt() -> None:
    hasher = HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()

    with pytest.raises(ValueError):
        hasher.hash_receipt(None)


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    HistoricalAdmissibilityEvidenceAdmissionReceiptHasher().hash_receipt(
        receipt
    )

    assert receipt == original
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False