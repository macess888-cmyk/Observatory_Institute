from datetime import datetime, timezone

import pytest

from models import TrustedKeyAdmissionReceipt
from services.trusted_key_admission_receipt_service import (
    TrustedKeyAdmissionReceiptError,
    TrustedKeyAdmissionReceiptService,
)


ADMITTED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)

MATERIAL_FINGERPRINT = "sha256:" + ("1" * 64)
SNAPSHOT_DIGEST = "sha256:" + ("2" * 64)


def make_receipt() -> TrustedKeyAdmissionReceipt:
    return TrustedKeyAdmissionReceiptService().create(
        receipt_id="TKAR-001",
        registry_id="TKR-001",
        registry_version="1.1.0",
        previous_registry_version="1.0.0",
        snapshot_id="TKRS-002",
        snapshot_digest=SNAPSHOT_DIGEST,
        material_id="PKM-003",
        key_id="KEY-003",
        public_key_fingerprint=MATERIAL_FINGERPRINT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        admitted_by="OBSERVATORY-INSTITUTE",
        admission_reason="Approved trusted-key admission.",
        admitted_at=ADMITTED_AT,
    )


def test_service_creates_admission_receipt() -> None:
    receipt = make_receipt()

    assert isinstance(receipt, TrustedKeyAdmissionReceipt)
    assert receipt.receipt_id == "TKAR-001"
    assert receipt.registry_id == "TKR-001"
    assert receipt.registry_version == "1.1.0"
    assert receipt.previous_registry_version == "1.0.0"
    assert receipt.snapshot_id == "TKRS-002"
    assert receipt.snapshot_digest == SNAPSHOT_DIGEST
    assert receipt.material_id == "PKM-003"
    assert receipt.key_id == "KEY-003"
    assert receipt.public_key_fingerprint == MATERIAL_FINGERPRINT
    assert receipt.owner_id == "PROCESS-LINEAGE-CLASSIFIER"
    assert receipt.issuer_id == "OBSERVATORY-INSTITUTE"
    assert receipt.admitted_by == "OBSERVATORY-INSTITUTE"
    assert receipt.admission_reason == (
        "Approved trusted-key admission."
    )
    assert receipt.admitted_at == ADMITTED_AT
    assert receipt.admitted is True
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises((AttributeError, TypeError)):
        receipt.admitted = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "registry_id",
        "registry_version",
        "previous_registry_version",
        "snapshot_id",
        "material_id",
        "key_id",
        "owner_id",
        "issuer_id",
        "admitted_by",
        "admission_reason",
    ],
)
def test_service_rejects_empty_identity_or_reason(
    field_name: str,
) -> None:
    arguments = {
        "receipt_id": "TKAR-001",
        "registry_id": "TKR-001",
        "registry_version": "1.1.0",
        "previous_registry_version": "1.0.0",
        "snapshot_id": "TKRS-002",
        "snapshot_digest": SNAPSHOT_DIGEST,
        "material_id": "PKM-003",
        "key_id": "KEY-003",
        "public_key_fingerprint": MATERIAL_FINGERPRINT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "admitted_by": "OBSERVATORY-INSTITUTE",
        "admission_reason": "Approved trusted-key admission.",
        "admitted_at": ADMITTED_AT,
    }
    arguments[field_name] = ""

    with pytest.raises(
        TrustedKeyAdmissionReceiptError,
        match=field_name,
    ):
        TrustedKeyAdmissionReceiptService().create(
            **arguments
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("snapshot_digest", "md5:invalid"),
        (
            "public_key_fingerprint",
            "sha256:" + ("z" * 64),
        ),
    ],
)
def test_service_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "receipt_id": "TKAR-001",
        "registry_id": "TKR-001",
        "registry_version": "1.1.0",
        "previous_registry_version": "1.0.0",
        "snapshot_id": "TKRS-002",
        "snapshot_digest": SNAPSHOT_DIGEST,
        "material_id": "PKM-003",
        "key_id": "KEY-003",
        "public_key_fingerprint": MATERIAL_FINGERPRINT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "admitted_by": "OBSERVATORY-INSTITUTE",
        "admission_reason": "Approved trusted-key admission.",
        "admitted_at": ADMITTED_AT,
    }
    arguments[field_name] = value

    with pytest.raises(
        TrustedKeyAdmissionReceiptError,
        match=field_name,
    ):
        TrustedKeyAdmissionReceiptService().create(
            **arguments
        )


def test_service_rejects_same_registry_version() -> None:
    with pytest.raises(
        TrustedKeyAdmissionReceiptError,
        match="registry version transition",
    ):
        TrustedKeyAdmissionReceiptService().create(
            receipt_id="TKAR-001",
            registry_id="TKR-001",
            registry_version="1.0.0",
            previous_registry_version="1.0.0",
            snapshot_id="TKRS-002",
            snapshot_digest=SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            admitted_by="OBSERVATORY-INSTITUTE",
            admission_reason="Approved trusted-key admission.",
            admitted_at=ADMITTED_AT,
        )


def test_service_rejects_naive_admitted_at() -> None:
    with pytest.raises(
        TrustedKeyAdmissionReceiptError,
        match="timezone-aware",
    ):
        TrustedKeyAdmissionReceiptService().create(
            receipt_id="TKAR-001",
            registry_id="TKR-001",
            registry_version="1.1.0",
            previous_registry_version="1.0.0",
            snapshot_id="TKRS-002",
            snapshot_digest=SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            admitted_by="OBSERVATORY-INSTITUTE",
            admission_reason="Approved trusted-key admission.",
            admitted_at=datetime(2026, 7, 15, 13, 0),
        )


def test_service_rejects_non_datetime_admitted_at() -> None:
    with pytest.raises(TypeError, match="admitted_at"):
        TrustedKeyAdmissionReceiptService().create(
            receipt_id="TKAR-001",
            registry_id="TKR-001",
            registry_version="1.1.0",
            previous_registry_version="1.0.0",
            snapshot_id="TKRS-002",
            snapshot_digest=SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            admitted_by="OBSERVATORY-INSTITUTE",
            admission_reason="Approved trusted-key admission.",
            admitted_at="2026-07-15T13:00:00Z",  # type: ignore[arg-type]
        )


def test_service_is_deterministic_for_same_inputs() -> None:
    assert make_receipt() == make_receipt()


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_receipt_records_admission_without_execution() -> None:
    receipt = make_receipt()

    assert receipt.admitted is True
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False