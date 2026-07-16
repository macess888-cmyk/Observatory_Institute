import pytest

from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)
from services.historical_admissibility_evidence_trust_receipt_hasher import (
    HistoricalAdmissibilityEvidenceTrustReceiptHasher,
)
from services.historical_admissibility_evidence_trust_receipt_validator import (
    HistoricalAdmissibilityEvidenceTrustReceiptValidator,
)


def make_receipt(
    *,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
    recorded_at: str = "2026-07-16T20:30:00Z",
) -> HistoricalAdmissibilityEvidenceTrustReceipt:
    return HistoricalAdmissibilityEvidenceTrustReceipt(
        receipt_id="HAETR-000001",
        assessment_id="HAETA-000001",
        assessment_hash="a" * 64,
        manifest_id="HAEPM-000001",
        manifest_hash="b" * 64,
        trust_status=trust_status,
        confidence_level=confidence_level,
        policy_version="historical-evidence-trust-v1",
        recorded_at=recorded_at,
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_receipt_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_receipt_hash() -> None:
    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    assert validator.validate(
        receipt=make_receipt(),
        expected_hash="c" * 64,
    ) is False


def test_validator_detects_modified_receipt() -> None:
    original = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(original)
    )

    modified = make_receipt(
        trust_status="PASS",
        confidence_level="HIGH",
    )

    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    assert validator.validate(
        receipt=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "trust_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_trust_statuses(
    trust_status: str,
) -> None:
    receipt = make_receipt(
        trust_status=trust_status,
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_receipt() -> None:
    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

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
    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    with pytest.raises(ValueError):
        validator.validate(
            receipt=make_receipt(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    receipt = make_receipt()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(receipt)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(receipt)
    )

    HistoricalAdmissibilityEvidenceTrustReceiptValidator().validate(
        receipt=receipt,
        expected_hash=expected_hash,
    )

    assert receipt == original
    assert receipt.trust_established is False
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_successful_validation_does_not_establish_trust() -> None:
    receipt = make_receipt(
        trust_status="PASS",
        confidence_level="HIGH",
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(receipt)
    )

    validator = HistoricalAdmissibilityEvidenceTrustReceiptValidator()

    assert validator.validate(
        receipt=receipt,
        expected_hash=expected_hash,
    ) is True

    assert receipt.trust_established is False
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False