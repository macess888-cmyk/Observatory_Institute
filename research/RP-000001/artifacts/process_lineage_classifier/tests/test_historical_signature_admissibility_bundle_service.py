import pytest

from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)
from models.historical_signature_admissibility_receipt import (
    HistoricalSignatureAdmissibilityReceipt,
)
from services.historical_signature_admissibility_bundle_service import (
    HistoricalSignatureAdmissibilityBundleService,
)
from services.historical_signature_admissibility_receipt_hasher import (
    HistoricalSignatureAdmissibilityReceiptHasher,
)


def make_receipt(
    *,
    admissibility_status: str = "PASS",
) -> HistoricalSignatureAdmissibilityReceipt:
    return HistoricalSignatureAdmissibilityReceipt(
        receipt_id="HSAR-000001",
        assessment_hash="a" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status=admissibility_status,
        policy_version="historical-signature-admissibility-v1",
        recorded_at="2026-07-16T17:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_creates_bundle_from_validated_receipt() -> None:
    receipt = make_receipt()
    receipt_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    service = HistoricalSignatureAdmissibilityBundleService()

    bundle = service.create_bundle(
        bundle_id="HSAB-000001",
        receipt=receipt,
        receipt_hash=receipt_hash,
        exported_at="2026-07-16T18:00:00Z",
    )

    assert isinstance(bundle, HistoricalSignatureAdmissibilityBundle)
    assert bundle.bundle_id == "HSAB-000001"
    assert bundle.receipt_id == receipt.receipt_id
    assert bundle.receipt_hash == receipt_hash
    assert bundle.assessment_hash == receipt.assessment_hash
    assert bundle.signature_id == receipt.signature_id
    assert bundle.key_id == receipt.key_id
    assert bundle.admissibility_status == receipt.admissibility_status
    assert bundle.policy_version == receipt.policy_version
    assert bundle.exported_at == "2026-07-16T18:00:00Z"


@pytest.mark.parametrize(
    "status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_preserves_receipt_status(
    status: str,
) -> None:
    receipt = make_receipt(
        admissibility_status=status,
    )
    receipt_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    bundle = HistoricalSignatureAdmissibilityBundleService().create_bundle(
        bundle_id="HSAB-000001",
        receipt=receipt,
        receipt_hash=receipt_hash,
        exported_at="2026-07-16T18:00:00Z",
    )

    assert bundle.admissibility_status == status


def test_service_rejects_none_receipt() -> None:
    service = HistoricalSignatureAdmissibilityBundleService()

    with pytest.raises(ValueError):
        service.create_bundle(
            bundle_id="HSAB-000001",
            receipt=None,
            receipt_hash="a" * 64,
            exported_at="2026-07-16T18:00:00Z",
        )


def test_service_rejects_non_matching_receipt_hash() -> None:
    receipt = make_receipt()

    service = HistoricalSignatureAdmissibilityBundleService()

    with pytest.raises(ValueError):
        service.create_bundle(
            bundle_id="HSAB-000001",
            receipt=receipt,
            receipt_hash="b" * 64,
            exported_at="2026-07-16T18:00:00Z",
        )


@pytest.mark.parametrize(
    "receipt_hash",
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
def test_service_rejects_invalid_receipt_hash(
    receipt_hash: str | None,
) -> None:
    service = HistoricalSignatureAdmissibilityBundleService()

    with pytest.raises(ValueError):
        service.create_bundle(
            bundle_id="HSAB-000001",
            receipt=make_receipt(),
            receipt_hash=receipt_hash,
            exported_at="2026-07-16T18:00:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    receipt = make_receipt()
    receipt_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    bundle = HistoricalSignatureAdmissibilityBundleService().create_bundle(
        bundle_id="HSAB-000001",
        receipt=receipt,
        receipt_hash=receipt_hash,
        exported_at="2026-07-16T18:00:00Z",
    )

    assert bundle.authorization_granted is False
    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False


def test_service_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    receipt_hash = (
        HistoricalSignatureAdmissibilityReceiptHasher()
        .hash_receipt(receipt)
    )

    HistoricalSignatureAdmissibilityBundleService().create_bundle(
        bundle_id="HSAB-000001",
        receipt=receipt,
        receipt_hash=receipt_hash,
        exported_at="2026-07-16T18:00:00Z",
    )

    assert receipt == original
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False