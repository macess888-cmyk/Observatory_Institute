from dataclasses import FrozenInstanceError

import pytest

from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)


def make_bundle() -> HistoricalSignatureAdmissibilityBundle:
    return HistoricalSignatureAdmissibilityBundle(
        bundle_id="HSAB-000001",
        receipt_id="HSAR-000001",
        receipt_hash="a" * 64,
        assessment_hash="b" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status="PASS",
        policy_version="historical-signature-admissibility-v1",
        exported_at="2026-07-16T18:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_bundle_records_portable_receipt_evidence() -> None:
    bundle = make_bundle()

    assert bundle.bundle_id == "HSAB-000001"
    assert bundle.receipt_id == "HSAR-000001"
    assert bundle.receipt_hash == "a" * 64
    assert bundle.assessment_hash == "b" * 64
    assert bundle.signature_id == "SIG-000001"
    assert bundle.key_id == "KEY-000001"
    assert bundle.admissibility_status == "PASS"
    assert bundle.policy_version == "historical-signature-admissibility-v1"
    assert bundle.exported_at == "2026-07-16T18:00:00Z"


def test_bundle_is_immutable() -> None:
    bundle = make_bundle()

    with pytest.raises(FrozenInstanceError):
        bundle.admissibility_status = "REJECT"  # type: ignore[misc]


@pytest.mark.parametrize(
    "status",
    ["PASS", "HOLD", "REJECT"],
)
def test_bundle_supports_all_admissibility_statuses(
    status: str,
) -> None:
    bundle = HistoricalSignatureAdmissibilityBundle(
        bundle_id="HSAB-000001",
        receipt_id="HSAR-000001",
        receipt_hash="a" * 64,
        assessment_hash="b" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status=status,
        policy_version="historical-signature-admissibility-v1",
        exported_at="2026-07-16T18:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    assert bundle.admissibility_status == status


@pytest.mark.parametrize(
    "field_name",
    [
        "bundle_id",
        "receipt_id",
        "receipt_hash",
        "assessment_hash",
        "signature_id",
        "key_id",
        "admissibility_status",
        "policy_version",
        "exported_at",
    ],
)
def test_bundle_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "bundle_id": "HSAB-000001",
        "receipt_id": "HSAR-000001",
        "receipt_hash": "a" * 64,
        "assessment_hash": "b" * 64,
        "signature_id": "SIG-000001",
        "key_id": "KEY-000001",
        "admissibility_status": "PASS",
        "policy_version": "historical-signature-admissibility-v1",
        "exported_at": "2026-07-16T18:00:00Z",
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityBundle(**values)


@pytest.mark.parametrize(
    "field_name, invalid_hash",
    [
        ("receipt_hash", "a" * 63),
        ("receipt_hash", "a" * 65),
        ("receipt_hash", "g" * 64),
        ("assessment_hash", "b" * 63),
        ("assessment_hash", "b" * 65),
        ("assessment_hash", "g" * 64),
    ],
)
def test_bundle_rejects_invalid_hashes(
    field_name: str,
    invalid_hash: str,
) -> None:
    values = {
        "bundle_id": "HSAB-000001",
        "receipt_id": "HSAR-000001",
        "receipt_hash": "a" * 64,
        "assessment_hash": "b" * 64,
        "signature_id": "SIG-000001",
        "key_id": "KEY-000001",
        "admissibility_status": "PASS",
        "policy_version": "historical-signature-admissibility-v1",
        "exported_at": "2026-07-16T18:00:00Z",
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = invalid_hash

    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityBundle(**values)


def test_bundle_rejects_unknown_admissibility_status() -> None:
    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityBundle(
            bundle_id="HSAB-000001",
            receipt_id="HSAR-000001",
            receipt_hash="a" * 64,
            assessment_hash="b" * 64,
            signature_id="SIG-000001",
            key_id="KEY-000001",
            admissibility_status="UNKNOWN",
            policy_version="historical-signature-admissibility-v1",
            exported_at="2026-07-16T18:00:00Z",
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
def test_bundle_rejects_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "bundle_id": "HSAB-000001",
        "receipt_id": "HSAR-000001",
        "receipt_hash": "a" * 64,
        "assessment_hash": "b" * 64,
        "signature_id": "SIG-000001",
        "key_id": "KEY-000001",
        "admissibility_status": "PASS",
        "policy_version": "historical-signature-admissibility-v1",
        "exported_at": "2026-07-16T18:00:00Z",
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalSignatureAdmissibilityBundle(**values)


def test_bundle_preserves_observer_only_invariants() -> None:
    bundle = make_bundle()

    assert bundle.authorization_granted is False
    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False