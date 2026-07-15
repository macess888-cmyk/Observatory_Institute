import hashlib
from datetime import datetime, timezone

import pytest

from models import SignatureVerificationReceipt
from services.signature_verification_receipt_hasher import (
    SignatureVerificationReceiptHashError,
    SignatureVerificationReceiptHasher,
)


VERIFIED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
PAYLOAD_DIGEST = "sha256:" + ("2" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("3" * 64)


def make_receipt(
    *,
    receipt_id: str = "SVR-001",
    verification_id: str = "SV-001",
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    subject_id: str = "RIB-001",
    verifier_id: str = "OBSERVATORY-INSTITUTE",
) -> SignatureVerificationReceipt:
    return SignatureVerificationReceipt(
        receipt_id=receipt_id,
        verification_id=verification_id,
        signature_id=signature_id,
        key_id=key_id,
        subject_id=subject_id,
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=CONTENT_DIGEST,
        payload_digest=PAYLOAD_DIGEST,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        algorithm="ED25519",
        signer_id="PROCESS-LINEAGE-CLASSIFIER",
        verifier_id=verifier_id,
        verified_at=VERIFIED_AT,
        mathematical_verification=True,
        identity_match=True,
        content_match=True,
        key_valid=True,
        verified=True,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    receipt = make_receipt()
    hasher = SignatureVerificationReceiptHasher()

    canonical = hasher.canonicalize(receipt)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(receipt) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = SignatureVerificationReceiptHasher().canonicalize(
        make_receipt()
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = SignatureVerificationReceiptHasher()
    receipt = make_receipt()

    first = hasher.hash(receipt)
    second = hasher.hash(receipt)

    assert first == second


def test_equivalent_receipts_produce_same_hash() -> None:
    hasher = SignatureVerificationReceiptHasher()

    assert hasher.hash(make_receipt()) == hasher.hash(
        make_receipt()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("receipt_id", "SVR-999"),
        ("verification_id", "SV-999"),
        ("signature_id", "SIG-999"),
        ("key_id", "KEY-999"),
        ("subject_id", "RIB-999"),
        ("verifier_id", "OTHER-VERIFIER"),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = SignatureVerificationReceiptHasher()

    baseline = hasher.hash(make_receipt())
    changed = hasher.hash(
        make_receipt(**{field_name: value})
    )

    assert baseline != changed


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        SignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_preserves_expected_field_order() -> None:
    canonical_text = (
        SignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    expected_order = (
        '"receipt_id"',
        '"verification_id"',
        '"signature_id"',
        '"key_id"',
        '"subject_id"',
        '"subject_type"',
        '"content_digest"',
        '"payload_digest"',
        '"public_key_fingerprint"',
        '"algorithm"',
        '"signer_id"',
        '"verifier_id"',
        '"verified_at"',
        '"mathematical_verification"',
        '"identity_match"',
        '"content_match"',
        '"key_valid"',
        '"verified"',
        '"execution_requested"',
        '"side_effects_permitted"',
    )

    positions = tuple(
        canonical_text.index(field_name)
        for field_name in expected_order
    )

    assert positions == tuple(sorted(positions))


def test_canonical_payload_uses_iso_timestamp() -> None:
    canonical_text = (
        SignatureVerificationReceiptHasher()
        .canonicalize(make_receipt())
        .decode("utf-8")
    )

    assert VERIFIED_AT.isoformat() in canonical_text


def test_hasher_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="SignatureVerificationReceipt",
    ):
        SignatureVerificationReceiptHasher().hash(
            "SVR-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="SignatureVerificationReceipt",
    ):
        SignatureVerificationReceiptHasher().canonicalize(
            "SVR-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = SignatureVerificationReceiptHasher()
    receipt = make_receipt()
    digest = hasher.hash(receipt)

    assert hasher.validate(receipt, digest) is True


def test_validate_rejects_digest_mismatch() -> None:
    with pytest.raises(
        SignatureVerificationReceiptHashError,
        match="hash mismatch",
    ):
        SignatureVerificationReceiptHasher().validate(
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
        SignatureVerificationReceiptHashError,
        match="expected_digest",
    ):
        SignatureVerificationReceiptHasher().validate(
            make_receipt(),
            digest,
        )


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    SignatureVerificationReceiptHasher().hash(receipt)

    assert receipt == original


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False