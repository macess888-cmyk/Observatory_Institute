import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import TrustedKeyAdmissionReceipt
from services.trusted_key_admission_receipt_hasher import (
    TrustedKeyAdmissionReceiptHashError,
    TrustedKeyAdmissionReceiptHasher,
)


ADMITTED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)

MATERIAL_FINGERPRINT = "sha256:" + ("1" * 64)
SNAPSHOT_DIGEST = "sha256:" + ("2" * 64)


def make_receipt(
    *,
    receipt_id: str = "TKAR-001",
    registry_id: str = "TKR-001",
    registry_version: str = "1.1.0",
    previous_registry_version: str = "1.0.0",
    snapshot_id: str = "TKRS-002",
    material_id: str = "PKM-003",
    key_id: str = "KEY-003",
    admitted_by: str = "OBSERVATORY-INSTITUTE",
    admission_reason: str = "Approved trusted-key admission.",
) -> TrustedKeyAdmissionReceipt:
    return TrustedKeyAdmissionReceipt(
        receipt_id=receipt_id,
        registry_id=registry_id,
        registry_version=registry_version,
        previous_registry_version=previous_registry_version,
        snapshot_id=snapshot_id,
        snapshot_digest=SNAPSHOT_DIGEST,
        material_id=material_id,
        key_id=key_id,
        public_key_fingerprint=MATERIAL_FINGERPRINT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        admitted_by=admitted_by,
        admission_reason=admission_reason,
        admitted_at=ADMITTED_AT,
        admitted=True,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    receipt = make_receipt()
    hasher = TrustedKeyAdmissionReceiptHasher()

    canonical = hasher.canonicalize(receipt)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(receipt) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = TrustedKeyAdmissionReceiptHasher().canonicalize(
        make_receipt()
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = TrustedKeyAdmissionReceiptHasher()
    receipt = make_receipt()

    assert hasher.hash(receipt) == hasher.hash(receipt)


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = TrustedKeyAdmissionReceiptHasher()

    assert hasher.hash(make_receipt()) == hasher.hash(
        make_receipt()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("receipt_id", "TKAR-999"),
        ("registry_id", "TKR-999"),
        ("registry_version", "2.0.0"),
        ("previous_registry_version", "0.9.0"),
        ("snapshot_id", "TKRS-999"),
        ("material_id", "PKM-999"),
        ("key_id", "KEY-999"),
        ("admitted_by", "OTHER-ADMITTER"),
        ("admission_reason", "Different reason."),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = TrustedKeyAdmissionReceiptHasher()

    baseline = hasher.hash(make_receipt())
    changed = hasher.hash(
        make_receipt(**{field_name: value})
    )

    assert baseline != changed


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        TrustedKeyAdmissionReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = (
        TrustedKeyAdmissionReceiptHasher()
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
        "snapshot_id",
        "snapshot_digest",
        "material_id",
        "key_id",
        "public_key_fingerprint",
        "owner_id",
        "issuer_id",
        "admitted_by",
        "admission_reason",
        "admitted_at",
        "admitted",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamp() -> None:
    canonical_text = (
        TrustedKeyAdmissionReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert ADMITTED_AT.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = TrustedKeyAdmissionReceiptHasher().canonicalize(
        make_receipt()
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["receipt_id"] == "TKAR-001"
    assert decoded["admitted"] is True
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyAdmissionReceipt",
    ):
        TrustedKeyAdmissionReceiptHasher().hash(
            "TKAR-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyAdmissionReceipt",
    ):
        TrustedKeyAdmissionReceiptHasher().canonicalize(
            "TKAR-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = TrustedKeyAdmissionReceiptHasher()
    receipt = make_receipt()
    digest = hasher.hash(receipt)

    assert hasher.validate(receipt, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        TrustedKeyAdmissionReceiptHashError,
        match="hash mismatch",
    ):
        TrustedKeyAdmissionReceiptHasher().validate(
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
        TrustedKeyAdmissionReceiptHashError,
        match="expected_digest",
    ):
        TrustedKeyAdmissionReceiptHasher().validate(
            make_receipt(),
            digest,
        )


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    TrustedKeyAdmissionReceiptHasher().hash(receipt)

    assert receipt == original


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.admitted is True
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False