import hashlib
import json

import pytest

from models.historical_signature_admissibility_receipt import (
    HistoricalSignatureAdmissibilityReceipt,
)
from services.historical_signature_admissibility_receipt_hasher import (
    HistoricalSignatureAdmissibilityReceiptHasher,
)


def make_receipt(
    *,
    receipt_id: str = "HSAR-000001",
    assessment_hash: str = "a" * 64,
    signature_id: str = "SIG-000001",
    key_id: str = "KEY-000001",
    admissibility_status: str = "PASS",
    policy_version: str = "historical-signature-admissibility-v1",
    recorded_at: str = "2026-07-16T17:00:00Z",
) -> HistoricalSignatureAdmissibilityReceipt:
    return HistoricalSignatureAdmissibilityReceipt(
        receipt_id=receipt_id,
        assessment_hash=assessment_hash,
        signature_id=signature_id,
        key_id=key_id,
        admissibility_status=admissibility_status,
        policy_version=policy_version,
        recorded_at=recorded_at,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    receipt: HistoricalSignatureAdmissibilityReceipt,
) -> str:
    payload = {
        "admissibility_status": receipt.admissibility_status,
        "assessment_hash": receipt.assessment_hash,
        "authorization_granted": receipt.authorization_granted,
        "execution_requested": receipt.execution_requested,
        "key_id": receipt.key_id,
        "policy_version": receipt.policy_version,
        "receipt_id": receipt.receipt_id,
        "recorded_at": receipt.recorded_at,
        "side_effects_permitted": receipt.side_effects_permitted,
        "signature_id": receipt.signature_id,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    receipt = make_receipt()
    hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    result = hasher.hash_receipt(receipt)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    receipt = make_receipt()
    hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    assert hasher.hash_receipt(receipt) == expected_hash(receipt)


def test_hasher_is_deterministic() -> None:
    receipt = make_receipt()
    hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    first = hasher.hash_receipt(receipt)
    second = hasher.hash_receipt(receipt)

    assert first == second


def test_equivalent_receipts_produce_same_hash() -> None:
    first = make_receipt()
    second = make_receipt()
    hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    assert hasher.hash_receipt(first) == hasher.hash_receipt(second)


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("receipt_id", "HSAR-000002"),
        ("assessment_hash", "b" * 64),
        ("signature_id", "SIG-000002"),
        ("key_id", "KEY-000002"),
        ("admissibility_status", "HOLD"),
        ("policy_version", "historical-signature-admissibility-v2"),
        ("recorded_at", "2026-07-16T18:00:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_receipt()

    changed_values = {
        "receipt_id": baseline.receipt_id,
        "assessment_hash": baseline.assessment_hash,
        "signature_id": baseline.signature_id,
        "key_id": baseline.key_id,
        "admissibility_status": baseline.admissibility_status,
        "policy_version": baseline.policy_version,
        "recorded_at": baseline.recorded_at,
    }
    changed_values[field_name] = changed_value

    changed = make_receipt(**changed_values)

    hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    assert hasher.hash_receipt(baseline) != hasher.hash_receipt(changed)


def test_hasher_rejects_none_receipt() -> None:
    hasher = HistoricalSignatureAdmissibilityReceiptHasher()

    with pytest.raises(ValueError):
        hasher.hash_receipt(None)


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    hasher = HistoricalSignatureAdmissibilityReceiptHasher()
    hasher.hash_receipt(receipt)

    assert receipt == original
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False