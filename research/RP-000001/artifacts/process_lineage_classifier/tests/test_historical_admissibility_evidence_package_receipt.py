from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_package_receipt import (
    HistoricalAdmissibilityEvidencePackageReceipt,
)


def make_receipt(
    *,
    package_status: str = "PASS",
) -> HistoricalAdmissibilityEvidencePackageReceipt:
    return HistoricalAdmissibilityEvidencePackageReceipt(
        receipt_id="HAEPKGR-000001",
        package_id="HAEPKG-000001",
        package_hash="a" * 64,
        package_status=package_status,
        package_version="historical-evidence-package-v1",
        recorded_at="2026-07-16T22:30:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_receipt_records_historical_evidence_package() -> None:
    receipt = make_receipt()

    assert receipt.receipt_id == "HAEPKGR-000001"
    assert receipt.package_id == "HAEPKG-000001"
    assert receipt.package_hash == "a" * 64
    assert receipt.package_status == "PASS"
    assert receipt.package_version == "historical-evidence-package-v1"
    assert receipt.recorded_at == "2026-07-16T22:30:00Z"


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises(FrozenInstanceError):
        receipt.package_status = "HOLD"  # type: ignore[misc]


@pytest.mark.parametrize(
    "package_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_receipt_supports_package_statuses(
    package_status: str,
) -> None:
    receipt = make_receipt(
        package_status=package_status,
    )

    assert receipt.package_status == package_status


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "package_id",
        "package_hash",
        "package_status",
        "package_version",
        "recorded_at",
    ],
)
def test_receipt_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "receipt_id": "HAEPKGR-000001",
        "package_id": "HAEPKG-000001",
        "package_hash": "a" * 64,
        "package_status": "PASS",
        "package_version": "historical-evidence-package-v1",
        "recorded_at": "2026-07-16T22:30:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackageReceipt(**values)


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_receipt_rejects_invalid_package_hash(
    invalid_hash: str,
) -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackageReceipt(
            receipt_id="HAEPKGR-000001",
            package_id="HAEPKG-000001",
            package_hash=invalid_hash,
            package_status="PASS",
            package_version="historical-evidence-package-v1",
            recorded_at="2026-07-16T22:30:00Z",
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_receipt_rejects_unknown_package_status() -> None:
    with pytest.raises(ValueError):
        make_receipt(
            package_status="UNKNOWN",
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
        "receipt_id": "HAEPKGR-000001",
        "package_id": "HAEPKG-000001",
        "package_hash": "a" * 64,
        "package_status": "PASS",
        "package_version": "historical-evidence-package-v1",
        "recorded_at": "2026-07-16T22:30:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackageReceipt(**values)


def test_receipt_preserves_observer_only_invariants() -> None:
    receipt = make_receipt()

    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False