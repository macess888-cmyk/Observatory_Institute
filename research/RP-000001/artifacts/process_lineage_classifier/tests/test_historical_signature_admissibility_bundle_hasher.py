import hashlib
import json

import pytest

from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)
from services.historical_signature_admissibility_bundle_hasher import (
    HistoricalSignatureAdmissibilityBundleHasher,
)


def make_bundle(
    *,
    bundle_id: str = "HSAB-000001",
    receipt_id: str = "HSAR-000001",
    receipt_hash: str = "a" * 64,
    assessment_hash: str = "b" * 64,
    signature_id: str = "SIG-000001",
    key_id: str = "KEY-000001",
    admissibility_status: str = "PASS",
    policy_version: str = "historical-signature-admissibility-v1",
    exported_at: str = "2026-07-16T18:00:00Z",
) -> HistoricalSignatureAdmissibilityBundle:
    return HistoricalSignatureAdmissibilityBundle(
        bundle_id=bundle_id,
        receipt_id=receipt_id,
        receipt_hash=receipt_hash,
        assessment_hash=assessment_hash,
        signature_id=signature_id,
        key_id=key_id,
        admissibility_status=admissibility_status,
        policy_version=policy_version,
        exported_at=exported_at,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    bundle: HistoricalSignatureAdmissibilityBundle,
) -> str:
    payload = {
        "admissibility_status": bundle.admissibility_status,
        "assessment_hash": bundle.assessment_hash,
        "authorization_granted": bundle.authorization_granted,
        "bundle_id": bundle.bundle_id,
        "execution_requested": bundle.execution_requested,
        "exported_at": bundle.exported_at,
        "key_id": bundle.key_id,
        "policy_version": bundle.policy_version,
        "receipt_hash": bundle.receipt_hash,
        "receipt_id": bundle.receipt_id,
        "side_effects_permitted": bundle.side_effects_permitted,
        "signature_id": bundle.signature_id,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    bundle = make_bundle()
    hasher = HistoricalSignatureAdmissibilityBundleHasher()

    result = hasher.hash_bundle(bundle)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    bundle = make_bundle()
    hasher = HistoricalSignatureAdmissibilityBundleHasher()

    assert hasher.hash_bundle(bundle) == expected_hash(bundle)


def test_hasher_is_deterministic() -> None:
    bundle = make_bundle()
    hasher = HistoricalSignatureAdmissibilityBundleHasher()

    assert hasher.hash_bundle(bundle) == hasher.hash_bundle(bundle)


def test_equivalent_bundles_produce_same_hash() -> None:
    hasher = HistoricalSignatureAdmissibilityBundleHasher()

    assert hasher.hash_bundle(make_bundle()) == hasher.hash_bundle(
        make_bundle()
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("bundle_id", "HSAB-000002"),
        ("receipt_id", "HSAR-000002"),
        ("receipt_hash", "c" * 64),
        ("assessment_hash", "d" * 64),
        ("signature_id", "SIG-000002"),
        ("key_id", "KEY-000002"),
        ("admissibility_status", "HOLD"),
        ("policy_version", "historical-signature-admissibility-v2"),
        ("exported_at", "2026-07-16T19:00:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_bundle()

    values = {
        "bundle_id": baseline.bundle_id,
        "receipt_id": baseline.receipt_id,
        "receipt_hash": baseline.receipt_hash,
        "assessment_hash": baseline.assessment_hash,
        "signature_id": baseline.signature_id,
        "key_id": baseline.key_id,
        "admissibility_status": baseline.admissibility_status,
        "policy_version": baseline.policy_version,
        "exported_at": baseline.exported_at,
    }
    values[field_name] = changed_value

    changed = make_bundle(**values)

    hasher = HistoricalSignatureAdmissibilityBundleHasher()

    assert hasher.hash_bundle(baseline) != hasher.hash_bundle(changed)


def test_hasher_rejects_none_bundle() -> None:
    hasher = HistoricalSignatureAdmissibilityBundleHasher()

    with pytest.raises(ValueError):
        hasher.hash_bundle(None)


def test_hasher_does_not_mutate_bundle() -> None:
    bundle = make_bundle()
    original = bundle

    HistoricalSignatureAdmissibilityBundleHasher().hash_bundle(bundle)

    assert bundle == original
    assert bundle.authorization_granted is False
    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False