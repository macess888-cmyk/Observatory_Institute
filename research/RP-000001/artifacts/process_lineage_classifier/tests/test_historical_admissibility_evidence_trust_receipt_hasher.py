import hashlib
import json

import pytest

from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)
from services.historical_admissibility_evidence_trust_receipt_hasher import (
    HistoricalAdmissibilityEvidenceTrustReceiptHasher,
)


def make_receipt(
    *,
    receipt_id: str = "HAETR-000001",
    assessment_id: str = "HAETA-000001",
    assessment_hash: str = "a" * 64,
    manifest_id: str = "HAEPM-000001",
    manifest_hash: str = "b" * 64,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
    policy_version: str = "historical-evidence-trust-v1",
    recorded_at: str = "2026-07-16T20:30:00Z",
) -> HistoricalAdmissibilityEvidenceTrustReceipt:
    return HistoricalAdmissibilityEvidenceTrustReceipt(
        receipt_id=receipt_id,
        assessment_id=assessment_id,
        assessment_hash=assessment_hash,
        manifest_id=manifest_id,
        manifest_hash=manifest_hash,
        trust_status=trust_status,
        confidence_level=confidence_level,
        policy_version=policy_version,
        recorded_at=recorded_at,
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    receipt: HistoricalAdmissibilityEvidenceTrustReceipt,
) -> str:
    payload = {
        "assessment_hash": receipt.assessment_hash,
        "assessment_id": receipt.assessment_id,
        "authorization_granted": receipt.authorization_granted,
        "confidence_level": receipt.confidence_level,
        "evidence_admitted": receipt.evidence_admitted,
        "execution_requested": receipt.execution_requested,
        "manifest_hash": receipt.manifest_hash,
        "manifest_id": receipt.manifest_id,
        "policy_version": receipt.policy_version,
        "receipt_id": receipt.receipt_id,
        "recorded_at": receipt.recorded_at,
        "side_effects_permitted": receipt.side_effects_permitted,
        "trust_established": receipt.trust_established,
        "trust_status": receipt.trust_status,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidenceTrustReceiptHasher()

    result = hasher.hash_receipt(receipt)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidenceTrustReceiptHasher()

    assert hasher.hash_receipt(receipt) == expected_hash(receipt)


def test_hasher_is_deterministic() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidenceTrustReceiptHasher()

    assert hasher.hash_receipt(receipt) == hasher.hash_receipt(receipt)


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidenceTrustReceiptHasher()

    assert hasher.hash_receipt(make_receipt()) == hasher.hash_receipt(
        make_receipt()
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("receipt_id", "HAETR-000002"),
        ("assessment_id", "HAETA-000002"),
        ("assessment_hash", "c" * 64),
        ("manifest_id", "HAEPM-000002"),
        ("manifest_hash", "d" * 64),
        ("trust_status", "PASS"),
        ("confidence_level", "HIGH"),
        ("policy_version", "historical-evidence-trust-v2"),
        ("recorded_at", "2026-07-16T20:31:00Z"),
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
        "manifest_id": baseline.manifest_id,
        "manifest_hash": baseline.manifest_hash,
        "trust_status": baseline.trust_status,
        "confidence_level": baseline.confidence_level,
        "policy_version": baseline.policy_version,
        "recorded_at": baseline.recorded_at,
    }
    values[field_name] = changed_value

    changed = make_receipt(**values)

    hasher = HistoricalAdmissibilityEvidenceTrustReceiptHasher()

    assert hasher.hash_receipt(baseline) != hasher.hash_receipt(changed)


def test_hasher_rejects_none_receipt() -> None:
    hasher = HistoricalAdmissibilityEvidenceTrustReceiptHasher()

    with pytest.raises(ValueError):
        hasher.hash_receipt(None)


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    HistoricalAdmissibilityEvidenceTrustReceiptHasher().hash_receipt(
        receipt
    )

    assert receipt == original
    assert receipt.trust_established is False
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False