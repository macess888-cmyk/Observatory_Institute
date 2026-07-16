import hashlib
import json

import pytest

from models.historical_admissibility_evidence_package_receipt import (
    HistoricalAdmissibilityEvidencePackageReceipt,
)
from services.historical_admissibility_evidence_package_receipt_hasher import (
    HistoricalAdmissibilityEvidencePackageReceiptHasher,
)


def make_receipt(
    *,
    receipt_id: str = "HAEPKGR-000001",
    package_id: str = "HAEPKG-000001",
    package_hash: str = "a" * 64,
    package_status: str = "PASS",
    package_version: str = "historical-evidence-package-v1",
    recorded_at: str = "2026-07-16T22:30:00Z",
) -> HistoricalAdmissibilityEvidencePackageReceipt:
    return HistoricalAdmissibilityEvidencePackageReceipt(
        receipt_id=receipt_id,
        package_id=package_id,
        package_hash=package_hash,
        package_status=package_status,
        package_version=package_version,
        recorded_at=recorded_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    receipt: HistoricalAdmissibilityEvidencePackageReceipt,
) -> str:
    payload = {
        "authorization_granted": receipt.authorization_granted,
        "evidence_admitted": receipt.evidence_admitted,
        "execution_requested": receipt.execution_requested,
        "package_hash": receipt.package_hash,
        "package_id": receipt.package_id,
        "package_status": receipt.package_status,
        "package_version": receipt.package_version,
        "receipt_id": receipt.receipt_id,
        "recorded_at": receipt.recorded_at,
        "side_effects_permitted": receipt.side_effects_permitted,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidencePackageReceiptHasher()

    result = hasher.hash_receipt(receipt)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidencePackageReceiptHasher()

    assert hasher.hash_receipt(receipt) == expected_hash(receipt)


def test_hasher_is_deterministic() -> None:
    receipt = make_receipt()
    hasher = HistoricalAdmissibilityEvidencePackageReceiptHasher()

    assert hasher.hash_receipt(receipt) == hasher.hash_receipt(receipt)


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidencePackageReceiptHasher()

    assert hasher.hash_receipt(make_receipt()) == hasher.hash_receipt(
        make_receipt()
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("receipt_id", "HAEPKGR-000002"),
        ("package_id", "HAEPKG-000002"),
        ("package_hash", "b" * 64),
        ("package_status", "HOLD"),
        ("package_version", "historical-evidence-package-v2"),
        ("recorded_at", "2026-07-16T22:31:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_receipt()

    values = {
        "receipt_id": baseline.receipt_id,
        "package_id": baseline.package_id,
        "package_hash": baseline.package_hash,
        "package_status": baseline.package_status,
        "package_version": baseline.package_version,
        "recorded_at": baseline.recorded_at,
    }
    values[field_name] = changed_value

    changed = make_receipt(**values)

    hasher = HistoricalAdmissibilityEvidencePackageReceiptHasher()

    assert hasher.hash_receipt(baseline) != hasher.hash_receipt(changed)


def test_hasher_rejects_none_receipt() -> None:
    hasher = HistoricalAdmissibilityEvidencePackageReceiptHasher()

    with pytest.raises(ValueError):
        hasher.hash_receipt(None)


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    HistoricalAdmissibilityEvidencePackageReceiptHasher().hash_receipt(
        receipt
    )

    assert receipt == original
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False