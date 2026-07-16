from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_package import (
    HistoricalAdmissibilityEvidencePackage,
)


def make_package() -> HistoricalAdmissibilityEvidencePackage:
    return HistoricalAdmissibilityEvidencePackage(
        package_id="HAEPKG-000001",
        admissibility_bundle_id="HSAB-000001",
        admissibility_bundle_hash="a" * 64,
        provenance_manifest_id="HAEPM-000001",
        provenance_manifest_hash="b" * 64,
        trust_receipt_id="HAETR-000001",
        trust_receipt_hash="c" * 64,
        admission_receipt_id="HAEAR-000001",
        admission_receipt_hash="d" * 64,
        package_version="historical-evidence-package-v1",
        assembled_at="2026-07-16T22:00:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_package_records_complete_historical_evidence_chain() -> None:
    package = make_package()

    assert package.package_id == "HAEPKG-000001"
    assert package.admissibility_bundle_id == "HSAB-000001"
    assert package.admissibility_bundle_hash == "a" * 64
    assert package.provenance_manifest_id == "HAEPM-000001"
    assert package.provenance_manifest_hash == "b" * 64
    assert package.trust_receipt_id == "HAETR-000001"
    assert package.trust_receipt_hash == "c" * 64
    assert package.admission_receipt_id == "HAEAR-000001"
    assert package.admission_receipt_hash == "d" * 64
    assert package.package_version == "historical-evidence-package-v1"
    assert package.assembled_at == "2026-07-16T22:00:00Z"


def test_package_is_immutable() -> None:
    package = make_package()

    with pytest.raises(FrozenInstanceError):
        package.package_version = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "package_id",
        "admissibility_bundle_id",
        "admissibility_bundle_hash",
        "provenance_manifest_id",
        "provenance_manifest_hash",
        "trust_receipt_id",
        "trust_receipt_hash",
        "admission_receipt_id",
        "admission_receipt_hash",
        "package_version",
        "assembled_at",
    ],
)
def test_package_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "package_id": "HAEPKG-000001",
        "admissibility_bundle_id": "HSAB-000001",
        "admissibility_bundle_hash": "a" * 64,
        "provenance_manifest_id": "HAEPM-000001",
        "provenance_manifest_hash": "b" * 64,
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "c" * 64,
        "admission_receipt_id": "HAEAR-000001",
        "admission_receipt_hash": "d" * 64,
        "package_version": "historical-evidence-package-v1",
        "assembled_at": "2026-07-16T22:00:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackage(**values)


@pytest.mark.parametrize(
    "field_name, invalid_hash",
    [
        ("admissibility_bundle_hash", "a" * 63),
        ("admissibility_bundle_hash", "a" * 65),
        ("admissibility_bundle_hash", "g" * 64),
        ("provenance_manifest_hash", "b" * 63),
        ("provenance_manifest_hash", "b" * 65),
        ("provenance_manifest_hash", "g" * 64),
        ("trust_receipt_hash", "c" * 63),
        ("trust_receipt_hash", "c" * 65),
        ("trust_receipt_hash", "g" * 64),
        ("admission_receipt_hash", "d" * 63),
        ("admission_receipt_hash", "d" * 65),
        ("admission_receipt_hash", "g" * 64),
    ],
)
def test_package_rejects_invalid_hashes(
    field_name: str,
    invalid_hash: str,
) -> None:
    values = {
        "package_id": "HAEPKG-000001",
        "admissibility_bundle_id": "HSAB-000001",
        "admissibility_bundle_hash": "a" * 64,
        "provenance_manifest_id": "HAEPM-000001",
        "provenance_manifest_hash": "b" * 64,
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "c" * 64,
        "admission_receipt_id": "HAEAR-000001",
        "admission_receipt_hash": "d" * 64,
        "package_version": "historical-evidence-package-v1",
        "assembled_at": "2026-07-16T22:00:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = invalid_hash

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackage(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "evidence_admitted",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_package_rejects_admission_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "package_id": "HAEPKG-000001",
        "admissibility_bundle_id": "HSAB-000001",
        "admissibility_bundle_hash": "a" * 64,
        "provenance_manifest_id": "HAEPM-000001",
        "provenance_manifest_hash": "b" * 64,
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "c" * 64,
        "admission_receipt_id": "HAEAR-000001",
        "admission_receipt_hash": "d" * 64,
        "package_version": "historical-evidence-package-v1",
        "assembled_at": "2026-07-16T22:00:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackage(**values)


def test_package_preserves_observer_only_invariants() -> None:
    package = make_package()

    assert package.evidence_admitted is False
    assert package.authorization_granted is False
    assert package.execution_requested is False
    assert package.side_effects_permitted is False