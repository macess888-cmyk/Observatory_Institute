import pytest

from models.historical_admissibility_evidence_package import (
    HistoricalAdmissibilityEvidencePackage,
)
from services.historical_admissibility_evidence_package_hasher import (
    HistoricalAdmissibilityEvidencePackageHasher,
)
from services.historical_admissibility_evidence_package_validator import (
    HistoricalAdmissibilityEvidencePackageValidator,
)


def make_package(
    *,
    assembled_at: str = "2026-07-16T22:00:00Z",
    package_version: str = "historical-evidence-package-v1",
) -> HistoricalAdmissibilityEvidencePackage:
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
        package_version=package_version,
        assembled_at=assembled_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_package_hash() -> None:
    package = make_package()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
    )

    validator = HistoricalAdmissibilityEvidencePackageValidator()

    assert validator.validate(
        package=package,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_package_hash() -> None:
    validator = HistoricalAdmissibilityEvidencePackageValidator()

    assert validator.validate(
        package=make_package(),
        expected_hash="e" * 64,
    ) is False


def test_validator_detects_modified_package() -> None:
    original = make_package()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(original)
    )

    modified = make_package(
        package_version="historical-evidence-package-v2",
    )

    validator = HistoricalAdmissibilityEvidencePackageValidator()

    assert validator.validate(
        package=modified,
        expected_hash=expected_hash,
    ) is False


def test_validator_rejects_none_package() -> None:
    validator = HistoricalAdmissibilityEvidencePackageValidator()

    with pytest.raises(ValueError):
        validator.validate(
            package=None,
            expected_hash="a" * 64,
        )


@pytest.mark.parametrize(
    "expected_hash",
    [
        None,
        "",
        " ",
        "abc",
        "g" * 64,
        "a" * 63,
        "a" * 65,
    ],
)
def test_validator_rejects_invalid_expected_hash(
    expected_hash: str | None,
) -> None:
    validator = HistoricalAdmissibilityEvidencePackageValidator()

    with pytest.raises(ValueError):
        validator.validate(
            package=make_package(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    package = make_package()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidencePackageValidator()

    assert validator.validate(
        package=package,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_package() -> None:
    package = make_package()
    original = package

    expected_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
    )

    HistoricalAdmissibilityEvidencePackageValidator().validate(
        package=package,
        expected_hash=expected_hash,
    )

    assert package == original
    assert package.evidence_admitted is False
    assert package.authorization_granted is False
    assert package.execution_requested is False
    assert package.side_effects_permitted is False


def test_successful_validation_does_not_admit_evidence() -> None:
    package = make_package()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
    )

    validator = HistoricalAdmissibilityEvidencePackageValidator()

    assert validator.validate(
        package=package,
        expected_hash=expected_hash,
    ) is True

    assert package.evidence_admitted is False
    assert package.authorization_granted is False
    assert package.execution_requested is False
    assert package.side_effects_permitted is False