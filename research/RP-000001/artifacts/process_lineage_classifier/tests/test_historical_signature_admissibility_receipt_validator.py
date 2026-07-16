import pytest

from models.historical_signature_admissibility_receipt import (
    HistoricalSignatureAdmissibilityReceipt,
)
from services.historical_signature_admissibility_receipt_hasher import (
    HistoricalSignatureAdmissibilityReceiptHasher,
)
from services.historical_signature_admissibility_receipt_validator import (
    HistoricalSignatureAdmissibilityReceiptValidator,
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


def test_validator_accepts_matching_receipt_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_receipt_hash() -> None:
    receipt = make_receipt()

    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash="b" * 64,
    ) is False


def test_validator_detects_modified_receipt() -> None:
    original = make_receipt()
    expected_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(original)
    )

    modified = make_receipt(
        admissibility_status="HOLD",
    )

    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    assert validator.validate(
        receipt=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_admissibility_statuses(
    status: str,
) -> None:
    receipt = make_receipt(
        admissibility_status=status,
    )
    expected_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_receipt() -> None:
    validator = HistoricalSignatureAdmissibilityReceiptValidator()

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
    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    with pytest.raises(ValueError):
        validator.validate(
            receipt=make_receipt(),
            expected_hash=expected_hash,
        )


def test_validator_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    expected_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    )

    assert receipt == original
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_successful_validation_does_not_grant_authority() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalSignatureAdmissibilityReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True

    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False