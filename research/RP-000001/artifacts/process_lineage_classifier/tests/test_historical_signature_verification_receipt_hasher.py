import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import HistoricalSignatureVerificationReceipt
from services.historical_signature_verification_receipt_hasher import (
    HistoricalSignatureVerificationReceiptHashError,
    HistoricalSignatureVerificationReceiptHasher,
)


SIGNED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 15, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
PAYLOAD_DIGEST = "sha256:" + ("2" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("3" * 64)
SIGNING_SNAPSHOT_DIGEST = "sha256:" + ("4" * 64)
VERIFICATION_SNAPSHOT_DIGEST = "sha256:" + ("5" * 64)


def make_receipt(
    *,
    receipt_id: str = "HSVR-001",
    verification_id: str = "HSV-001",
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    signing_registry_version: str = "1.0.0",
    verification_registry_version: str = "1.2.0",
    signing_snapshot_id: str = "TKRS-100",
    verification_snapshot_id: str = "TKRS-120",
    verification_time_key_present: bool = False,
) -> HistoricalSignatureVerificationReceipt:
    return HistoricalSignatureVerificationReceipt(
        receipt_id=receipt_id,
        verification_id=verification_id,
        signature_id=signature_id,
        key_id=key_id,
        subject_id="RIB-001",
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=CONTENT_DIGEST,
        payload_digest=PAYLOAD_DIGEST,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        algorithm="ED25519",
        signer_id="PROCESS-LINEAGE-CLASSIFIER",
        verifier_id="OBSERVATORY-INSTITUTE",
        registry_id="TKR-001",
        signing_registry_version=signing_registry_version,
        signing_snapshot_id=signing_snapshot_id,
        signing_snapshot_digest=SIGNING_SNAPSHOT_DIGEST,
        verification_registry_version=verification_registry_version,
        verification_snapshot_id=verification_snapshot_id,
        verification_snapshot_digest=VERIFICATION_SNAPSHOT_DIGEST,
        signed_at=SIGNED_AT,
        verified_at=VERIFIED_AT,
        mathematical_verification=True,
        identity_match=True,
        content_match=True,
        signing_time_key_present=True,
        verification_time_key_present=verification_time_key_present,
        key_valid_at_signing=True,
        verified=True,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    receipt = make_receipt()
    hasher = HistoricalSignatureVerificationReceiptHasher()

    canonical = hasher.canonicalize(receipt)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(receipt) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = (
        HistoricalSignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = HistoricalSignatureVerificationReceiptHasher()
    receipt = make_receipt()

    assert hasher.hash(receipt) == hasher.hash(receipt)


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = HistoricalSignatureVerificationReceiptHasher()

    assert hasher.hash(make_receipt()) == hasher.hash(
        make_receipt()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("receipt_id", "HSVR-999"),
        ("verification_id", "HSV-999"),
        ("signature_id", "SIG-999"),
        ("key_id", "KEY-999"),
        ("signing_registry_version", "0.9.0"),
        ("verification_registry_version", "2.0.0"),
        ("signing_snapshot_id", "TKRS-099"),
        ("verification_snapshot_id", "TKRS-999"),
        ("verification_time_key_present", True),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: object,
) -> None:
    hasher = HistoricalSignatureVerificationReceiptHasher()

    baseline = hasher.hash(make_receipt())
    changed = hasher.hash(
        make_receipt(**{field_name: value})
    )

    assert baseline != changed


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        HistoricalSignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = (
        HistoricalSignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
    )

    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )

    assert tuple(decoded.keys()) == (
        "receipt_id",
        "verification_id",
        "signature_id",
        "key_id",
        "subject_id",
        "subject_type",
        "content_digest",
        "payload_digest",
        "public_key_fingerprint",
        "algorithm",
        "signer_id",
        "verifier_id",
        "registry_id",
        "signing_registry_version",
        "signing_snapshot_id",
        "signing_snapshot_digest",
        "verification_registry_version",
        "verification_snapshot_id",
        "verification_snapshot_digest",
        "signed_at",
        "verified_at",
        "mathematical_verification",
        "identity_match",
        "content_match",
        "signing_time_key_present",
        "verification_time_key_present",
        "key_valid_at_signing",
        "verified",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamps() -> None:
    canonical_text = (
        HistoricalSignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert SIGNED_AT.isoformat() in canonical_text
    assert VERIFIED_AT.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = (
        HistoricalSignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["receipt_id"] == "HSVR-001"
    assert decoded["signing_time_key_present"] is True
    assert decoded["verification_time_key_present"] is False
    assert decoded["verified"] is True
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureVerificationReceipt",
    ):
        HistoricalSignatureVerificationReceiptHasher().hash(
            "HSVR-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureVerificationReceipt",
    ):
        HistoricalSignatureVerificationReceiptHasher().canonicalize(
            "HSVR-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = HistoricalSignatureVerificationReceiptHasher()
    receipt = make_receipt()
    digest = hasher.hash(receipt)

    assert hasher.validate(receipt, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        HistoricalSignatureVerificationReceiptHashError,
        match="hash mismatch",
    ):
        HistoricalSignatureVerificationReceiptHasher().validate(
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
        HistoricalSignatureVerificationReceiptHashError,
        match="expected_digest",
    ):
        HistoricalSignatureVerificationReceiptHasher().validate(
            make_receipt(),
            digest,
        )


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    HistoricalSignatureVerificationReceiptHasher().hash(
        receipt
    )

    assert receipt == original


def test_hash_preserves_non_retroactive_boundary() -> None:
    receipt = make_receipt()
    canonical = (
        HistoricalSignatureVerificationReceiptHasher()
        .canonicalize(receipt)
    )
    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["signing_time_key_present"] is True
    assert decoded["verification_time_key_present"] is False
    assert decoded["verified"] is True


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False