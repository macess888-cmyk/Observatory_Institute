import pytest

from models.historical_admissibility_evidence_admission_receipt import (
    HistoricalAdmissibilityEvidenceAdmissionReceipt,
)
from services.historical_admissibility_evidence_admission_receipt_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptHasher,
)
from services.historical_admissibility_evidence_admission_receipt_validator import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptValidator,
)


def make_receipt(
    *,
    admission_status: str = "HOLD",
    recorded_at: str = "2026-07-16T21:30:00Z",
) -> HistoricalAdmissibilityEvidenceAdmissionReceipt:
    return HistoricalAdmissibilityEvidenceAdmissionReceipt(
        receipt_id="HAEAR-000001",
        assessment_id="HAEAA-000001",
        assessment_hash="a" * 64,
        trust_receipt_id="HAETR-000001",
        trust_receipt_hash="b" * 64,
        admission_status=admission_status,
        policy_version="historical-evidence-admission-v1",
        recorded_at=recorded_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_receipt_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_receipt_hash() -> None:
    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    assert validator.validate(
        receipt=make_receipt(),
        expected_hash="c" * 64,
    ) is False


def test_validator_detects_modified_receipt() -> None:
    original = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(original)
    )

    modified = make_receipt(
        admission_status="PASS",
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    assert validator.validate(
        receipt=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "admission_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_admission_statuses(
    admission_status: str,
) -> None:
    receipt = make_receipt(
        admission_status=admission_status,
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_receipt() -> None:
    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

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
    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    with pytest.raises(ValueError):
        validator.validate(
            receipt=make_receipt(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(receipt)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(receipt)
    )

    HistoricalAdmissibilityEvidenceAdmissionReceiptValidator().validate(
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
        admission_status="PASS",
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True

    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False