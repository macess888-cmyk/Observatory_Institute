from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)


def make_receipt(
    *,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
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
        recorded_at="2026-07-16T20:30:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_receipt_records_trust_assessment() -> None:
    receipt = make_receipt()

    assert receipt.receipt_id == "HAETR-000001"
    assert receipt.assessment_id == "HAETA-000001"
    assert receipt.assessment_hash == "a" * 64
    assert receipt.manifest_id == "HAEPM-000001"
    assert receipt.manifest_hash == "b" * 64
    assert receipt.trust_status == "HOLD"
    assert receipt.confidence_level == "MEDIUM"
    assert receipt.policy_version == "historical-evidence-trust-v1"
    assert receipt.recorded_at == "2026-07-16T20:30:00Z"


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises(FrozenInstanceError):
        receipt.trust_status = "PASS"  # type: ignore[misc]


@pytest.mark.parametrize(
    "trust_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_receipt_supports_trust_statuses(
    trust_status: str,
) -> None:
    receipt = make_receipt(
        trust_status=trust_status,
    )

    assert receipt.trust_status == trust_status


@pytest.mark.parametrize(
    "confidence_level",
    ["LOW", "MEDIUM", "HIGH"],
)
def test_receipt_supports_confidence_levels(
    confidence_level: str,
) -> None:
    receipt = make_receipt(
        confidence_level=confidence_level,
    )

    assert receipt.confidence_level == confidence_level


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "assessment_id",
        "assessment_hash",
        "manifest_id",
        "manifest_hash",
        "trust_status",
        "confidence_level",
        "policy_version",
        "recorded_at",
    ],
)
def test_receipt_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "receipt_id": "HAETR-000001",
        "assessment_id": "HAETA-000001",
        "assessment_hash": "a" * 64,
        "manifest_id": "HAEPM-000001",
        "manifest_hash": "b" * 64,
        "trust_status": "HOLD",
        "confidence_level": "MEDIUM",
        "policy_version": "historical-evidence-trust-v1",
        "recorded_at": "2026-07-16T20:30:00Z",
        "trust_established": False,
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustReceipt(**values)


@pytest.mark.parametrize(
    "field_name, invalid_hash",
    [
        ("assessment_hash", "a" * 63),
        ("assessment_hash", "a" * 65),
        ("assessment_hash", "g" * 64),
        ("manifest_hash", "b" * 63),
        ("manifest_hash", "b" * 65),
        ("manifest_hash", "g" * 64),
    ],
)
def test_receipt_rejects_invalid_hashes(
    field_name: str,
    invalid_hash: str,
) -> None:
    values = {
        "receipt_id": "HAETR-000001",
        "assessment_id": "HAETA-000001",
        "assessment_hash": "a" * 64,
        "manifest_id": "HAEPM-000001",
        "manifest_hash": "b" * 64,
        "trust_status": "HOLD",
        "confidence_level": "MEDIUM",
        "policy_version": "historical-evidence-trust-v1",
        "recorded_at": "2026-07-16T20:30:00Z",
        "trust_established": False,
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = invalid_hash

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustReceipt(**values)


def test_receipt_rejects_unknown_trust_status() -> None:
    with pytest.raises(ValueError):
        make_receipt(
            trust_status="UNKNOWN",
        )


def test_receipt_rejects_unknown_confidence_level() -> None:
    with pytest.raises(ValueError):
        make_receipt(
            confidence_level="CERTAIN",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "trust_established",
        "evidence_admitted",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_receipt_rejects_trust_admission_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "receipt_id": "HAETR-000001",
        "assessment_id": "HAETA-000001",
        "assessment_hash": "a" * 64,
        "manifest_id": "HAEPM-000001",
        "manifest_hash": "b" * 64,
        "trust_status": "HOLD",
        "confidence_level": "MEDIUM",
        "policy_version": "historical-evidence-trust-v1",
        "recorded_at": "2026-07-16T20:30:00Z",
        "trust_established": False,
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustReceipt(**values)


def test_receipt_preserves_observer_only_invariants() -> None:
    receipt = make_receipt()

    assert receipt.trust_established is False
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False