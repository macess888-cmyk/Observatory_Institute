import hashlib
import json

import pytest

from models.historical_admissibility_evidence_package import (
    HistoricalAdmissibilityEvidencePackage,
)
from services.historical_admissibility_evidence_package_hasher import (
    HistoricalAdmissibilityEvidencePackageHasher,
)


def make_package(
    *,
    package_id: str = "HAEPKG-000001",
    admissibility_bundle_id: str = "HSAB-000001",
    admissibility_bundle_hash: str = "a" * 64,
    provenance_manifest_id: str = "HAEPM-000001",
    provenance_manifest_hash: str = "b" * 64,
    trust_receipt_id: str = "HAETR-000001",
    trust_receipt_hash: str = "c" * 64,
    admission_receipt_id: str = "HAEAR-000001",
    admission_receipt_hash: str = "d" * 64,
    package_version: str = "historical-evidence-package-v1",
    assembled_at: str = "2026-07-16T22:00:00Z",
) -> HistoricalAdmissibilityEvidencePackage:
    return HistoricalAdmissibilityEvidencePackage(
        package_id=package_id,
        admissibility_bundle_id=admissibility_bundle_id,
        admissibility_bundle_hash=admissibility_bundle_hash,
        provenance_manifest_id=provenance_manifest_id,
        provenance_manifest_hash=provenance_manifest_hash,
        trust_receipt_id=trust_receipt_id,
        trust_receipt_hash=trust_receipt_hash,
        admission_receipt_id=admission_receipt_id,
        admission_receipt_hash=admission_receipt_hash,
        package_version=package_version,
        assembled_at=assembled_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    package: HistoricalAdmissibilityEvidencePackage,
) -> str:
    payload = {
        "admissibility_bundle_hash": package.admissibility_bundle_hash,
        "admissibility_bundle_id": package.admissibility_bundle_id,
        "admission_receipt_hash": package.admission_receipt_hash,
        "admission_receipt_id": package.admission_receipt_id,
        "assembled_at": package.assembled_at,
        "authorization_granted": package.authorization_granted,
        "evidence_admitted": package.evidence_admitted,
        "execution_requested": package.execution_requested,
        "package_id": package.package_id,
        "package_version": package.package_version,
        "provenance_manifest_hash": package.provenance_manifest_hash,
        "provenance_manifest_id": package.provenance_manifest_id,
        "side_effects_permitted": package.side_effects_permitted,
        "trust_receipt_hash": package.trust_receipt_hash,
        "trust_receipt_id": package.trust_receipt_id,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    package = make_package()
    hasher = HistoricalAdmissibilityEvidencePackageHasher()

    result = hasher.hash_package(package)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    package = make_package()
    hasher = HistoricalAdmissibilityEvidencePackageHasher()

    assert hasher.hash_package(package) == expected_hash(package)


def test_hasher_is_deterministic() -> None:
    package = make_package()
    hasher = HistoricalAdmissibilityEvidencePackageHasher()

    assert hasher.hash_package(package) == hasher.hash_package(package)


def test_equivalent_packages_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidencePackageHasher()

    assert hasher.hash_package(make_package()) == hasher.hash_package(
        make_package()
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("package_id", "HAEPKG-000002"),
        ("admissibility_bundle_id", "HSAB-000002"),
        ("admissibility_bundle_hash", "e" * 64),
        ("provenance_manifest_id", "HAEPM-000002"),
        ("provenance_manifest_hash", "f" * 64),
        ("trust_receipt_id", "HAETR-000002"),
        ("trust_receipt_hash", "1" * 64),
        ("admission_receipt_id", "HAEAR-000002"),
        ("admission_receipt_hash", "2" * 64),
        ("package_version", "historical-evidence-package-v2"),
        ("assembled_at", "2026-07-16T22:01:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_package()

    values = {
        "package_id": baseline.package_id,
        "admissibility_bundle_id": baseline.admissibility_bundle_id,
        "admissibility_bundle_hash": baseline.admissibility_bundle_hash,
        "provenance_manifest_id": baseline.provenance_manifest_id,
        "provenance_manifest_hash": baseline.provenance_manifest_hash,
        "trust_receipt_id": baseline.trust_receipt_id,
        "trust_receipt_hash": baseline.trust_receipt_hash,
        "admission_receipt_id": baseline.admission_receipt_id,
        "admission_receipt_hash": baseline.admission_receipt_hash,
        "package_version": baseline.package_version,
        "assembled_at": baseline.assembled_at,
    }
    values[field_name] = changed_value

    changed = make_package(**values)

    hasher = HistoricalAdmissibilityEvidencePackageHasher()

    assert hasher.hash_package(baseline) != hasher.hash_package(changed)


def test_hasher_rejects_none_package() -> None:
    hasher = HistoricalAdmissibilityEvidencePackageHasher()

    with pytest.raises(ValueError):
        hasher.hash_package(None)


def test_hasher_does_not_mutate_package() -> None:
    package = make_package()
    original = package

    HistoricalAdmissibilityEvidencePackageHasher().hash_package(package)

    assert package == original
    assert package.evidence_admitted is False
    assert package.authorization_granted is False
    assert package.execution_requested is False
    assert package.side_effects_permitted is False