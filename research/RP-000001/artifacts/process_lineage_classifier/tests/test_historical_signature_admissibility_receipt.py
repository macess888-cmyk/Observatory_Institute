from dataclasses import FrozenInstanceError

import pytest

from models.historical_signature_admissibility_receipt import (
    HistoricalSignatureAdmissibilityReceipt,
)


def make_receipt() -> HistoricalSignatureAdmissibilityReceipt:
    return HistoricalSignatureAdmissibilityReceipt(
        receipt_id="HSAR-000001",
        assessment_hash="a" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status="PASS",
        policy_version="historical-signature-admissibility-v1",
        recorded_at="2026-07-16T17:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_receipt_records_historical_admissibility_assessment() -> None:
    receipt = make_receipt()

    assert receipt.receipt_id == "HSAR-000001"
    assert receipt.assessment_hash == "a" * 64
    assert receipt.signature_id == "SIG-000001"
    assert receipt.key_id == "KEY-000001"
    assert receipt.admissibility_status == "PASS"
    assert receipt.policy_version == "historical-signature-admissibility-v1"
    assert receipt.recorded_at == "2026-07-16T17:00:00Z"


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises(FrozenInstanceError):
        receipt.admissibility_status = "REJECT"  # type: ignore[misc]


def test_receipt_does_not_grant_authorization() -> None:
    receipt = make_receipt()

    assert receipt.authorization_granted is False


def test_receipt_does_not_request_execution() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False


def test_receipt_does_not_permit_side_effects() -> None:
    receipt = make_receipt()

    assert receipt.side_effects_permitted is False


@pytest.mark.parametrize("status", ["PASS", "HOLD", "REJECT"])
def test_receipt_supports_admissibility_statuses(status: str) -> None:
    receipt = HistoricalSignatureAdmissibilityReceipt(
        receipt_id="HSAR-000001",
        assessment_hash="a" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status=status,
        policy_version="historical-signature-admissibility-v1",
        recorded_at="2026-07-16T17:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    assert receipt.admissibility_status == status


@pytest.mark.parametrize(
    "field_name, invalid_value",
    [
        ("receipt_id", ""),
        ("assessment_hash", ""),
        ("signature_id", ""),
        ("key_id", ""),
        ("admissibility_status", ""),
        ("policy_version", ""),
        ("recorded_at", ""),
    ],
)
def test_receipt_rejects_empty_required_fields(
    field_name: str,
    invalid_value: str,
) -> None:
    values = {
        "receipt_id": "HSAR-000001",
        "assessment_hash": "a" * 64,
        "signature_id": "SIG-000001",
        "key_id": "KEY-000001",
        "admissibility_status": "PASS",
        "policy_version": "historical-signature-admissibility-v1",
        "recorded_at": "2026-07-16T17:00:00Z",
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = invalid_value

    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityReceipt(**values)


def test_receipt_rejects_unknown_admissibility_status() -> None:
    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityReceipt(
            receipt_id="HSAR-000001",
            assessment_hash="a" * 64,
            signature_id="SIG-000001",
            key_id="KEY-000001",
            admissibility_status="UNKNOWN",
            policy_version="historical-signature-admissibility-v1",
            recorded_at="2026-07-16T17:00:00Z",
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_receipt_rejects_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "receipt_id": "HSAR-000001",
        "assessment_hash": "a" * 64,
        "signature_id": "SIG-000001",
        "key_id": "KEY-000001",
        "admissibility_status": "PASS",
        "policy_version": "historical-signature-admissibility-v1",
        "recorded_at": "2026-07-16T17:00:00Z",
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityReceipt(**values)