import pytest

from models.historical_admissibility_evidence_package import (
    HistoricalAdmissibilityEvidencePackage,
)
from models.historical_admissibility_evidence_package_receipt import (
    HistoricalAdmissibilityEvidencePackageReceipt,
)
from services.historical_admissibility_evidence_package_hasher import (
    HistoricalAdmissibilityEvidencePackageHasher,
)
from services.historical_admissibility_evidence_package_receipt_service import (
    HistoricalAdmissibilityEvidencePackageReceiptService,
)


def make_package() -> HistoricalAdmissibilityEvidencePackage:
    return HistoricalAdmissibilityEvidencePackage(
        package_id="HAEPKG-000001",
        admissibility_bundle_id="HSAB-000001",
        admissibility_bundle_hash="a" * 64,
        provenance_manifest_id="HAEPM-000001",
        provenance_manifest_hash="b" * 64,
        trust_receipt_id="HAETR-000001",
        trust_receipt_hash="c" * 64,
        admission_receipt_id="HAEAR-000001",
        admission_receipt_hash="d" * 64,
        package_version="historical-evidence-package-v1",
        assembled_at="2026-07-16T22:00:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def create_receipt(
    *,
    package_status: str = "PASS",
) -> HistoricalAdmissibilityEvidencePackageReceipt:
    package = make_package()
    package_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
    )

    return HistoricalAdmissibilityEvidencePackageReceiptService().create_receipt(
        receipt_id="HAEPKGR-000001",
        package=package,
        package_hash=package_hash,
        package_status=package_status,
        recorded_at="2026-07-16T22:30:00Z",
    )


def test_service_creates_receipt_from_validated_package() -> None:
    receipt = create_receipt()

    assert isinstance(
        receipt,
        HistoricalAdmissibilityEvidencePackageReceipt,
    )
    assert receipt.receipt_id == "HAEPKGR-000001"
    assert receipt.package_id == "HAEPKG-000001"
    assert receipt.package_status == "PASS"
    assert receipt.package_version == "historical-evidence-package-v1"
    assert receipt.recorded_at == "2026-07-16T22:30:00Z"


@pytest.mark.parametrize(
    "package_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_preserves_package_status(
    package_status: str,
) -> None:
    receipt = create_receipt(
        package_status=package_status,
    )

    assert receipt.package_status == package_status


def test_service_rejects_none_package() -> None:
    service = HistoricalAdmissibilityEvidencePackageReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAEPKGR-000001",
            package=None,
            package_hash="a" * 64,
            package_status="PASS",
            recorded_at="2026-07-16T22:30:00Z",
        )


def test_service_rejects_non_matching_package_hash() -> None:
    service = HistoricalAdmissibilityEvidencePackageReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAEPKGR-000001",
            package=make_package(),
            package_hash="e" * 64,
            package_status="PASS",
            recorded_at="2026-07-16T22:30:00Z",
        )


@pytest.mark.parametrize(
    "package_hash",
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
def test_service_rejects_invalid_package_hash(
    package_hash: str | None,
) -> None:
    service = HistoricalAdmissibilityEvidencePackageReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAEPKGR-000001",
            package=make_package(),
            package_hash=package_hash,
            package_status="PASS",
            recorded_at="2026-07-16T22:30:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    receipt = create_receipt(
        package_status="PASS",
    )

    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_service_does_not_mutate_package() -> None:
    package = make_package()
    original = package
    package_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
    )

    HistoricalAdmissibilityEvidencePackageReceiptService().create_receipt(
        receipt_id="HAEPKGR-000001",
        package=package,
        package_hash=package_hash,
        package_status="PASS",
        recorded_at="2026-07-16T22:30:00Z",
    )

    assert package == original
    assert package.evidence_admitted is False
    assert package.authorization_granted is False
    assert package.execution_requested is False
    assert package.side_effects_permitted is False


def test_pass_receipt_does_not_admit_evidence() -> None:
    receipt = create_receipt(
        package_status="PASS",
    )

    assert receipt.package_status == "PASS"
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False