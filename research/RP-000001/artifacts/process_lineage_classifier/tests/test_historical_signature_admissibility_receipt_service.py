import pytest

from models.historical_signature_admissibility_receipt import (
    HistoricalSignatureAdmissibilityReceipt,
)
from services.historical_signature_admissibility_receipt_service import (
    HistoricalSignatureAdmissibilityReceiptService,
)


class StubAssessment:
    assessment_id = "HSAA-000001"
    assessment_hash = "a" * 64
    signature_id = "SIG-000001"
    key_id = "KEY-000001"
    admissibility_status = "PASS"
    policy_version = "historical-signature-admissibility-v1"


def test_service_creates_receipt_from_assessment() -> None:
    service = HistoricalSignatureAdmissibilityReceiptService()

    receipt = service.create_receipt(
        receipt_id="HSAR-000001",
        assessment=StubAssessment(),
        recorded_at="2026-07-16T17:00:00Z",
    )

    assert isinstance(receipt, HistoricalSignatureAdmissibilityReceipt)
    assert receipt.receipt_id == "HSAR-000001"
    assert receipt.assessment_hash == "a" * 64
    assert receipt.signature_id == "SIG-000001"
    assert receipt.key_id == "KEY-000001"
    assert receipt.admissibility_status == "PASS"
    assert receipt.policy_version == "historical-signature-admissibility-v1"
    assert receipt.recorded_at == "2026-07-16T17:00:00Z"


def test_service_preserves_observer_only_invariants() -> None:
    service = HistoricalSignatureAdmissibilityReceiptService()

    receipt = service.create_receipt(
        receipt_id="HSAR-000001",
        assessment=StubAssessment(),
        recorded_at="2026-07-16T17:00:00Z",
    )

    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


@pytest.mark.parametrize(
    "status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_preserves_assessment_status(status: str) -> None:
    class Assessment:
        assessment_hash = "a" * 64
        signature_id = "SIG-000001"
        key_id = "KEY-000001"
        admissibility_status = status
        policy_version = "historical-signature-admissibility-v1"

    service = HistoricalSignatureAdmissibilityReceiptService()

    receipt = service.create_receipt(
        receipt_id="HSAR-000001",
        assessment=Assessment(),
        recorded_at="2026-07-16T17:00:00Z",
    )

    assert receipt.admissibility_status == status


@pytest.mark.parametrize(
    "attribute_name",
    [
        "assessment_hash",
        "signature_id",
        "key_id",
        "admissibility_status",
        "policy_version",
    ],
)
def test_service_rejects_missing_assessment_attributes(
    attribute_name: str,
) -> None:
    attributes = {
        "assessment_hash": "a" * 64,
        "signature_id": "SIG-000001",
        "key_id": "KEY-000001",
        "admissibility_status": "PASS",
        "policy_version": "historical-signature-admissibility-v1",
    }
    del attributes[attribute_name]

    Assessment = type("Assessment", (), attributes)

    service = HistoricalSignatureAdmissibilityReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HSAR-000001",
            assessment=Assessment(),
            recorded_at="2026-07-16T17:00:00Z",
        )


def test_service_rejects_none_assessment() -> None:
    service = HistoricalSignatureAdmissibilityReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HSAR-000001",
            assessment=None,
            recorded_at="2026-07-16T17:00:00Z",
        )


def test_service_does_not_mutate_assessment() -> None:
    assessment = StubAssessment()

    original_values = {
        "assessment_id": assessment.assessment_id,
        "assessment_hash": assessment.assessment_hash,
        "signature_id": assessment.signature_id,
        "key_id": assessment.key_id,
        "admissibility_status": assessment.admissibility_status,
        "policy_version": assessment.policy_version,
    }

    service = HistoricalSignatureAdmissibilityReceiptService()

    service.create_receipt(
        receipt_id="HSAR-000001",
        assessment=assessment,
        recorded_at="2026-07-16T17:00:00Z",
    )

    current_values = {
        "assessment_id": assessment.assessment_id,
        "assessment_hash": assessment.assessment_hash,
        "signature_id": assessment.signature_id,
        "key_id": assessment.key_id,
        "admissibility_status": assessment.admissibility_status,
        "policy_version": assessment.policy_version,
    }

    assert current_values == original_values