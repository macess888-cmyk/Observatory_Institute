import pytest

from models.historical_admissibility_evidence_package_receipt import (
    HistoricalAdmissibilityEvidencePackageReceipt,
)
from services.historical_admissibility_evidence_package_receipt_hasher import (
    HistoricalAdmissibilityEvidencePackageReceiptHasher,
)
from services.historical_admissibility_evidence_package_receipt_validator import (
    HistoricalAdmissibilityEvidencePackageReceiptValidator,
)


def make_receipt(
    *,
    package_status: str = "PASS",
    recorded_at: str = "2026-07-16T22:30:00Z",
) -> HistoricalAdmissibilityEvidencePackageReceipt:
    return HistoricalAdmissibilityEvidencePackageReceipt(
        receipt_id="HAEPKGR-000001",
        package_id="HAEPKG-000001",
        package_hash="a" * 64,
        package_status=package_status,
        package_version="historical-evidence-package-v1",
        recorded_at=recorded_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_receipt_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_receipt_hash() -> None:
    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    assert validator.validate(
        receipt=make_receipt(),
        expected_hash="b" * 64,
    ) is False


def test_validator_detects_modified_receipt() -> None:
    original = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(original)
    )

    modified = make_receipt(
        package_status="HOLD",
    )

    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    assert validator.validate(
        receipt=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "package_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_package_statuses(
    package_status: str,
) -> None:
    receipt = make_receipt(
        package_status=package_status,
    )
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_receipt() -> None:
    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    with pytest.raises(ValueError):
        validator.validate(
            receipt=None,
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
    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    with pytest.raises(ValueError):
        validator.validate(
            receipt=make_receipt(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(receipt)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    expected_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(receipt)
    )

    HistoricalAdmissibilityEvidencePackageReceiptValidator().validate(
        receipt=receipt,
        expected_hash=expected_hash,
    )

    assert receipt == original
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_successful_validation_does_not_admit_evidence() -> None:
    receipt = make_receipt(
        package_status="PASS",
    )
    expected_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidencePackageReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True

    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False