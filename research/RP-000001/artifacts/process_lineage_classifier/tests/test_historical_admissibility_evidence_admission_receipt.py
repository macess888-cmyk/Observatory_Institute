from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_admission_receipt import (
    HistoricalAdmissibilityEvidenceAdmissionReceipt,
)


def make_receipt(
    *,
    admission_status: str = "HOLD",
) -> HistoricalAdmissibilityEvidenceAdmissionReceipt:
    return HistoricalAdmissibilityEvidenceAdmissionReceipt(
        receipt_id="HAEAR-000001",
        assessment_id="HAEAA-000001",
        assessment_hash="a" * 64,
        trust_receipt_id="HAETR-000001",
        trust_receipt_hash="b" * 64,
        admission_status=admission_status,
        policy_version="historical-evidence-admission-v1",
        recorded_at="2026-07-16T21:30:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_receipt_records_admission_assessment() -> None:
    receipt = make_receipt()

    assert receipt.receipt_id == "HAEAR-000001"
    assert receipt.assessment_id == "HAEAA-000001"
    assert receipt.assessment_hash == "a" * 64
    assert receipt.trust_receipt_id == "HAETR-000001"
    assert receipt.trust_receipt_hash == "b" * 64
    assert receipt.admission_status == "HOLD"
    assert receipt.policy_version == "historical-evidence-admission-v1"
    assert receipt.recorded_at == "2026-07-16T21:30:00Z"


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises(FrozenInstanceError):
        receipt.admission_status = "PASS"  # type: ignore[misc]


@pytest.mark.parametrize(
    "admission_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_receipt_supports_admission_statuses(
    admission_status: str,
) -> None:
    receipt = make_receipt(
        admission_status=admission_status,
    )

    assert receipt.admission_status == admission_status


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "assessment_id",
        "assessment_hash",
        "trust_receipt_id",
        "trust_receipt_hash",
        "admission_status",
        "policy_version",
        "recorded_at",
    ],
)
def test_receipt_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "receipt_id": "HAEAR-000001",
        "assessment_id": "HAEAA-000001",
        "assessment_hash": "a" * 64,
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "b" * 64,
        "admission_status": "HOLD",
        "policy_version": "historical-evidence-admission-v1",
        "recorded_at": "2026-07-16T21:30:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceAdmissionReceipt(**values)


@pytest.mark.parametrize(
    "field_name, invalid_hash",
    [
        ("assessment_hash", "a" * 63),
        ("assessment_hash", "a" * 65),
        ("assessment_hash", "g" * 64),
        ("trust_receipt_hash", "b" * 63),
        ("trust_receipt_hash", "b" * 65),
        ("trust_receipt_hash", "g" * 64),
    ],
)
def test_receipt_rejects_invalid_hashes(
    field_name: str,
    invalid_hash: str,
) -> None:
    values = {
        "receipt_id": "HAEAR-000001",
        "assessment_id": "HAEAA-000001",
        "assessment_hash": "a" * 64,
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "b" * 64,
        "admission_status": "HOLD",
        "policy_version": "historical-evidence-admission-v1",
        "recorded_at": "2026-07-16T21:30:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = invalid_hash

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceAdmissionReceipt(**values)


def test_receipt_rejects_unknown_admission_status() -> None:
    with pytest.raises(ValueError):
        make_receipt(
            admission_status="UNKNOWN",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "evidence_admitted",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_receipt_rejects_admission_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "receipt_id": "HAEAR-000001",
        "assessment_id": "HAEAA-000001",
        "assessment_hash": "a" * 64,
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "b" * 64,
        "admission_status": "HOLD",
        "policy_version": "historical-evidence-admission-v1",
        "recorded_at": "2026-07-16T21:30:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceAdmissionReceipt(**values)


def test_receipt_preserves_observer_only_invariants() -> None:
    receipt = make_receipt(
        admission_status="PASS",
    )

    assert receipt.admission_status == "PASS"
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False