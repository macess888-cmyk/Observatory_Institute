import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import TrustedKeyRemovalReceipt
from services.trusted_key_removal_receipt_hasher import (
    TrustedKeyRemovalReceiptHashError,
    TrustedKeyRemovalReceiptHasher,
)


REMOVED_AT = datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)

MATERIAL_FINGERPRINT = "sha256:" + ("1" * 64)
PREVIOUS_SNAPSHOT_DIGEST = "sha256:" + ("2" * 64)
CURRENT_SNAPSHOT_DIGEST = "sha256:" + ("3" * 64)


def make_receipt(
    *,
    receipt_id: str = "TKRR-001",
    registry_id: str = "TKR-001",
    registry_version: str = "1.2.0",
    previous_registry_version: str = "1.1.0",
    previous_snapshot_id: str = "TKRS-002",
    current_snapshot_id: str = "TKRS-003",
    material_id: str = "PKM-003",
    key_id: str = "KEY-003",
    removed_by: str = "OBSERVATORY-INSTITUTE",
    removal_reason: str = "Trusted-key removal approved.",
) -> TrustedKeyRemovalReceipt:
    return TrustedKeyRemovalReceipt(
        receipt_id=receipt_id,
        registry_id=registry_id,
        registry_version=registry_version,
        previous_registry_version=previous_registry_version,
        previous_snapshot_id=previous_snapshot_id,
        previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
        current_snapshot_id=current_snapshot_id,
        current_snapshot_digest=CURRENT_SNAPSHOT_DIGEST,
        material_id=material_id,
        key_id=key_id,
        public_key_fingerprint=MATERIAL_FINGERPRINT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        removed_by=removed_by,
        removal_reason=removal_reason,
        removed_at=REMOVED_AT,
        removed=True,
        retroactive_invalidation=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    receipt = make_receipt()
    hasher = TrustedKeyRemovalReceiptHasher()

    canonical = hasher.canonicalize(receipt)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(receipt) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = TrustedKeyRemovalReceiptHasher().canonicalize(
        make_receipt()
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = TrustedKeyRemovalReceiptHasher()
    receipt = make_receipt()

    assert hasher.hash(receipt) == hasher.hash(receipt)


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = TrustedKeyRemovalReceiptHasher()

    assert hasher.hash(make_receipt()) == hasher.hash(
        make_receipt()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("receipt_id", "TKRR-999"),
        ("registry_id", "TKR-999"),
        ("registry_version", "2.0.0"),
        ("previous_registry_version", "1.0.0"),
        ("previous_snapshot_id", "TKRS-001"),
        ("current_snapshot_id", "TKRS-999"),
        ("material_id", "PKM-999"),
        ("key_id", "KEY-999"),
        ("removed_by", "OTHER-REMOVER"),
        ("removal_reason", "Different removal reason."),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = TrustedKeyRemovalReceiptHasher()

    baseline = hasher.hash(make_receipt())
    changed = hasher.hash(
        make_receipt(**{field_name: value})
    )

    assert baseline != changed


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        TrustedKeyRemovalReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = (
        TrustedKeyRemovalReceiptHasher()
        .canonicalize(make_receipt())
    )

    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )

    assert tuple(decoded.keys()) == (
        "receipt_id",
        "registry_id",
        "registry_version",
        "previous_registry_version",
        "previous_snapshot_id",
        "previous_snapshot_digest",
        "current_snapshot_id",
        "current_snapshot_digest",
        "material_id",
        "key_id",
        "public_key_fingerprint",
        "owner_id",
        "issuer_id",
        "removed_by",
        "removal_reason",
        "removed_at",
        "removed",
        "retroactive_invalidation",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamp() -> None:
    canonical_text = (
        TrustedKeyRemovalReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert REMOVED_AT.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = TrustedKeyRemovalReceiptHasher().canonicalize(
        make_receipt()
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["receipt_id"] == "TKRR-001"
    assert decoded["removed"] is True
    assert decoded["retroactive_invalidation"] is False
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyRemovalReceipt",
    ):
        TrustedKeyRemovalReceiptHasher().hash(
            "TKRR-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyRemovalReceipt",
    ):
        TrustedKeyRemovalReceiptHasher().canonicalize(
            "TKRR-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = TrustedKeyRemovalReceiptHasher()
    receipt = make_receipt()
    digest = hasher.hash(receipt)

    assert hasher.validate(receipt, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptHashError,
        match="hash mismatch",
    ):
        TrustedKeyRemovalReceiptHasher().validate(
            make_receipt(),
            "sha256:" + ("9" * 64),
        )


@pytest.mark.parametrize(
    "digest",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
        "sha256:" + ("A" * 64),
    ],
)
def test_validate_rejects_invalid_expected_digest(
    digest: str,
) -> None:
    with pytest.raises(
        TrustedKeyRemovalReceiptHashError,
        match="expected_digest",
    ):
        TrustedKeyRemovalReceiptHasher().validate(
            make_receipt(),
            digest,
        )


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    TrustedKeyRemovalReceiptHasher().hash(receipt)

    assert receipt == original


def test_hash_preserves_non_retroactive_boundary() -> None:
    receipt = make_receipt()
    canonical = TrustedKeyRemovalReceiptHasher().canonicalize(
        receipt
    )
    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["removed"] is True
    assert decoded["retroactive_invalidation"] is False


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False