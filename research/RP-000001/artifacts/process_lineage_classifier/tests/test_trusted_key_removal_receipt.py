from datetime import datetime, timezone

import pytest

from models import TrustedKeyRemovalReceipt
from services.trusted_key_removal_receipt_service import (
    TrustedKeyRemovalReceiptError,
    TrustedKeyRemovalReceiptService,
)


REMOVED_AT = datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)

MATERIAL_FINGERPRINT = "sha256:" + ("1" * 64)
PREVIOUS_SNAPSHOT_DIGEST = "sha256:" + ("2" * 64)
CURRENT_SNAPSHOT_DIGEST = "sha256:" + ("3" * 64)


def make_receipt() -> TrustedKeyRemovalReceipt:
    return TrustedKeyRemovalReceiptService().create(
        receipt_id="TKRR-001",
        registry_id="TKR-001",
        registry_version="1.2.0",
        previous_registry_version="1.1.0",
        previous_snapshot_id="TKRS-002",
        previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
        current_snapshot_id="TKRS-003",
        current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
        material_id="PKM-003",
        key_id="KEY-003",
        public_key_fingerprint=MATERIAL_FINGERPRINT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        removed_by="OBSERVATORY-INSTITUTE",
        removal_reason="Trusted-key removal approved.",
        removed_at=REMOVED_AT,
        retroactive_invalidation=False,
    )


def test_service_creates_removal_receipt() -> None:
    receipt = make_receipt()

    assert isinstance(receipt, TrustedKeyRemovalReceipt)
    assert receipt.receipt_id == "TKRR-001"
    assert receipt.registry_id == "TKR-001"
    assert receipt.registry_version == "1.2.0"
    assert receipt.previous_registry_version == "1.1.0"
    assert receipt.previous_snapshot_id == "TKRS-002"
    assert receipt.previous_snapshot_digest == PREVIOUS_SNAPSHOT_DIGEST
    assert receipt.current_snapshot_id == "TKRS-003"
    assert receipt.current_snapshot_digest == CURRENT_SNAPSHOT_DIGEST
    assert receipt.material_id == "PKM-003"
    assert receipt.key_id == "KEY-003"
    assert receipt.public_key_fingerprint == MATERIAL_FINGERPRINT
    assert receipt.owner_id == "PROCESS-LINEAGE-CLASSIFIER"
    assert receipt.issuer_id == "OBSERVATORY-INSTITUTE"
    assert receipt.removed_by == "OBSERVATORY-INSTITUTE"
    assert receipt.removal_reason == "Trusted-key removal approved."
    assert receipt.removed_at == REMOVED_AT
    assert receipt.removed is True
    assert receipt.retroactive_invalidation is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises((AttributeError, TypeError)):
        receipt.removed = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "registry_id",
        "registry_version",
        "previous_registry_version",
        "previous_snapshot_id",
        "current_snapshot_id",
        "material_id",
        "key_id",
        "owner_id",
        "issuer_id",
        "removed_by",
        "removal_reason",
    ],
)
def test_service_rejects_empty_identity_or_reason(
    field_name: str,
) -> None:
    arguments = {
        "receipt_id": "TKRR-001",
        "registry_id": "TKR-001",
        "registry_version": "1.2.0",
        "previous_registry_version": "1.1.0",
        "previous_snapshot_id": "TKRS-002",
        "previous_snapshot_digest": PREVIOUS_SNAPSHOT_DIGEST,
        "current_snapshot_id": "TKRS-003",
        "current_snapshot_digest": CURRENT_SNAPSHOT_DIGEST,
        "material_id": "PKM-003",
        "key_id": "KEY-003",
        "public_key_fingerprint": MATERIAL_FINGERPRINT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "removed_by": "OBSERVATORY-INSTITUTE",
        "removal_reason": "Trusted-key removal approved.",
        "removed_at": REMOVED_AT,
        "retroactive_invalidation": False,
    }
    arguments[field_name] = ""

    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match=field_name,
    ):
        TrustedKeyRemovalReceiptService().create(**arguments)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("previous_snapshot_digest", "md5:invalid"),
        ("current_snapshot_digest", "sha256:abc"),
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
        "receipt_id": "TKRR-001",
        "registry_id": "TKR-001",
        "registry_version": "1.2.0",
        "previous_registry_version": "1.1.0",
        "previous_snapshot_id": "TKRS-002",
        "previous_snapshot_digest": PREVIOUS_SNAPSHOT_DIGEST,
        "current_snapshot_id": "TKRS-003",
        "current_snapshot_digest": CURRENT_SNAPSHOT_DIGEST,
        "material_id": "PKM-003",
        "key_id": "KEY-003",
        "public_key_fingerprint": MATERIAL_FINGERPRINT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "removed_by": "OBSERVATORY-INSTITUTE",
        "removal_reason": "Trusted-key removal approved.",
        "removed_at": REMOVED_AT,
        "retroactive_invalidation": False,
    }
    arguments[field_name] = value

    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match=field_name,
    ):
        TrustedKeyRemovalReceiptService().create(**arguments)


def test_service_rejects_same_registry_version() -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match="registry version transition",
    ):
        TrustedKeyRemovalReceiptService().create(
            receipt_id="TKRR-001",
            registry_id="TKR-001",
            registry_version="1.1.0",
            previous_registry_version="1.1.0",
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            current_snapshot_id="TKRS-003",
            current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            removed_by="OBSERVATORY-INSTITUTE",
            removal_reason="Trusted-key removal approved.",
            removed_at=REMOVED_AT,
            retroactive_invalidation=False,
        )


def test_service_rejects_same_snapshot_identity() -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match="snapshot transition",
    ):
        TrustedKeyRemovalReceiptService().create(
            receipt_id="TKRR-001",
            registry_id="TKR-001",
            registry_version="1.2.0",
            previous_registry_version="1.1.0",
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            current_snapshot_id="TKRS-002",
            current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            removed_by="OBSERVATORY-INSTITUTE",
            removal_reason="Trusted-key removal approved.",
            removed_at=REMOVED_AT,
            retroactive_invalidation=False,
        )


def test_service_rejects_same_snapshot_digest() -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match="snapshot digest transition",
    ):
        TrustedKeyRemovalReceiptService().create(
            receipt_id="TKRR-001",
            registry_id="TKR-001",
            registry_version="1.2.0",
            previous_registry_version="1.1.0",
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            current_snapshot_id="TKRS-003",
            current_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            removed_by="OBSERVATORY-INSTITUTE",
            removal_reason="Trusted-key removal approved.",
            removed_at=REMOVED_AT,
            retroactive_invalidation=False,
        )


def test_service_rejects_naive_removed_at() -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match="timezone-aware",
    ):
        TrustedKeyRemovalReceiptService().create(
            receipt_id="TKRR-001",
            registry_id="TKR-001",
            registry_version="1.2.0",
            previous_registry_version="1.1.0",
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            current_snapshot_id="TKRS-003",
            current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            removed_by="OBSERVATORY-INSTITUTE",
            removal_reason="Trusted-key removal approved.",
            removed_at=datetime(2026, 7, 15, 14, 0),
            retroactive_invalidation=False,
        )


def test_service_rejects_non_boolean_retroactive_invalidation() -> None:
    with pytest.raises(
        TypeError,
        match="retroactive_invalidation",
    ):
        TrustedKeyRemovalReceiptService().create(
            receipt_id="TKRR-001",
            registry_id="TKR-001",
            registry_version="1.2.0",
            previous_registry_version="1.1.0",
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            current_snapshot_id="TKRS-003",
            current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            removed_by="OBSERVATORY-INSTITUTE",
            removal_reason="Trusted-key removal approved.",
            removed_at=REMOVED_AT,
            retroactive_invalidation="false",  # type: ignore[arg-type]
        )


def test_service_rejects_retroactive_invalidation() -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptError,
        match="retroactive invalidation",
    ):
        TrustedKeyRemovalReceiptService().create(
            receipt_id="TKRR-001",
            registry_id="TKR-001",
            registry_version="1.2.0",
            previous_registry_version="1.1.0",
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            current_snapshot_id="TKRS-003",
            current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
            material_id="PKM-003",
            key_id="KEY-003",
            public_key_fingerprint=MATERIAL_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            removed_by="OBSERVATORY-INSTITUTE",
            removal_reason="Trusted-key removal approved.",
            removed_at=REMOVED_AT,
            retroactive_invalidation=True,
        )


def test_service_is_deterministic_for_same_inputs() -> None:
    assert make_receipt() == make_receipt()


def test_removal_does_not_claim_historical_invalidity() -> None:
    receipt = make_receipt()

    assert receipt.removed is True
    assert receipt.retroactive_invalidation is False


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False