from datetime import datetime, timezone

import pytest

from models import SignatureVerificationReceipt
from services.signature_verification_receipt_service import (
    SignatureVerificationReceiptError,
    SignatureVerificationReceiptService,
)


VERIFIED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("2" * 64)
PAYLOAD_DIGEST = "sha256:" + ("3" * 64)


def make_receipt() -> SignatureVerificationReceipt:
    return SignatureVerificationReceiptService().create(
        receipt_id="SVR-001",
        verification_id="SV-001",
        signature_id="SIG-001",
        key_id="KEY-001",
        subject_id="RIB-001",
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=CONTENT_DIGEST,
        payload_digest=PAYLOAD_DIGEST,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        algorithm="ED25519",
        signer_id="PROCESS-LINEAGE-CLASSIFIER",
        verifier_id="OBSERVATORY-INSTITUTE",
        verified_at=VERIFIED_AT,
        mathematical_verification=True,
        identity_match=True,
        content_match=True,
        key_valid=True,
    )


def test_service_creates_verified_receipt() -> None:
    receipt = make_receipt()

    assert isinstance(receipt, SignatureVerificationReceipt)
    assert receipt.receipt_id == "SVR-001"
    assert receipt.verification_id == "SV-001"
    assert receipt.signature_id == "SIG-001"
    assert receipt.key_id == "KEY-001"
    assert receipt.subject_id == "RIB-001"
    assert receipt.subject_type == "RECOVERY_INTEGRITY_BUNDLE"
    assert receipt.content_digest == CONTENT_DIGEST
    assert receipt.payload_digest == PAYLOAD_DIGEST
    assert receipt.public_key_fingerprint == PUBLIC_KEY_FINGERPRINT
    assert receipt.algorithm == "ED25519"
    assert receipt.signer_id == "PROCESS-LINEAGE-CLASSIFIER"
    assert receipt.verifier_id == "OBSERVATORY-INSTITUTE"
    assert receipt.mathematical_verification is True
    assert receipt.identity_match is True
    assert receipt.content_match is True
    assert receipt.key_valid is True
    assert receipt.verified is True
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_receipt_is_immutable() -> None:
    receipt = make_receipt()

    with pytest.raises((AttributeError, TypeError)):
        receipt.verified = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "verification_id",
        "signature_id",
        "key_id",
        "subject_id",
        "subject_type",
        "algorithm",
        "signer_id",
        "verifier_id",
    ],
)
def test_service_rejects_empty_identity_field(
    field_name: str,
) -> None:
    arguments = {
        "receipt_id": "SVR-001",
        "verification_id": "SV-001",
        "signature_id": "SIG-001",
        "key_id": "KEY-001",
        "subject_id": "RIB-001",
        "subject_type": "RECOVERY_INTEGRITY_BUNDLE",
        "content_digest": CONTENT_DIGEST,
        "payload_digest": PAYLOAD_DIGEST,
        "public_key_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "algorithm": "ED25519",
        "signer_id": "PROCESS-LINEAGE-CLASSIFIER",
        "verifier_id": "OBSERVATORY-INSTITUTE",
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "key_valid": True,
    }
    arguments[field_name] = ""

    with pytest.raises(
        SignatureVerificationReceiptError,
        match=field_name,
    ):
        SignatureVerificationReceiptService().create(**arguments)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("content_digest", "md5:invalid"),
        ("payload_digest", "sha256:abc"),
        (
            "public_key_fingerprint",
            "sha256:" + ("z" * 64),
        ),
    ],
)
def test_service_rejects_invalid_digest_or_fingerprint(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "receipt_id": "SVR-001",
        "verification_id": "SV-001",
        "signature_id": "SIG-001",
        "key_id": "KEY-001",
        "subject_id": "RIB-001",
        "subject_type": "RECOVERY_INTEGRITY_BUNDLE",
        "content_digest": CONTENT_DIGEST,
        "payload_digest": PAYLOAD_DIGEST,
        "public_key_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "algorithm": "ED25519",
        "signer_id": "PROCESS-LINEAGE-CLASSIFIER",
        "verifier_id": "OBSERVATORY-INSTITUTE",
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "key_valid": True,
    }
    arguments[field_name] = value

    with pytest.raises(
        SignatureVerificationReceiptError,
        match=field_name,
    ):
        SignatureVerificationReceiptService().create(**arguments)


def test_service_rejects_unsupported_algorithm() -> None:
    with pytest.raises(
        SignatureVerificationReceiptError,
        match="algorithm",
    ):
        SignatureVerificationReceiptService().create(
            receipt_id="SVR-001",
            verification_id="SV-001",
            signature_id="SIG-001",
            key_id="KEY-001",
            subject_id="RIB-001",
            subject_type="RECOVERY_INTEGRITY_BUNDLE",
            content_digest=CONTENT_DIGEST,
            payload_digest=PAYLOAD_DIGEST,
            public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
            algorithm="RSA",
            signer_id="PROCESS-LINEAGE-CLASSIFIER",
            verifier_id="OBSERVATORY-INSTITUTE",
            verified_at=VERIFIED_AT,
            mathematical_verification=True,
            identity_match=True,
            content_match=True,
            key_valid=True,
        )


def test_service_rejects_naive_verified_at() -> None:
    with pytest.raises(
        SignatureVerificationReceiptError,
        match="timezone-aware",
    ):
        SignatureVerificationReceiptService().create(
            receipt_id="SVR-001",
            verification_id="SV-001",
            signature_id="SIG-001",
            key_id="KEY-001",
            subject_id="RIB-001",
            subject_type="RECOVERY_INTEGRITY_BUNDLE",
            content_digest=CONTENT_DIGEST,
            payload_digest=PAYLOAD_DIGEST,
            public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
            algorithm="ED25519",
            signer_id="PROCESS-LINEAGE-CLASSIFIER",
            verifier_id="OBSERVATORY-INSTITUTE",
            verified_at=datetime(2026, 7, 15, 12, 0),
            mathematical_verification=True,
            identity_match=True,
            content_match=True,
            key_valid=True,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "mathematical_verification",
        "identity_match",
        "content_match",
        "key_valid",
    ],
)
def test_service_rejects_non_boolean_verification_component(
    field_name: str,
) -> None:
    arguments = {
        "receipt_id": "SVR-001",
        "verification_id": "SV-001",
        "signature_id": "SIG-001",
        "key_id": "KEY-001",
        "subject_id": "RIB-001",
        "subject_type": "RECOVERY_INTEGRITY_BUNDLE",
        "content_digest": CONTENT_DIGEST,
        "payload_digest": PAYLOAD_DIGEST,
        "public_key_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "algorithm": "ED25519",
        "signer_id": "PROCESS-LINEAGE-CLASSIFIER",
        "verifier_id": "OBSERVATORY-INSTITUTE",
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "key_valid": True,
    }
    arguments[field_name] = "true"

    with pytest.raises(TypeError, match=field_name):
        SignatureVerificationReceiptService().create(**arguments)


@pytest.mark.parametrize(
    "field_name",
    [
        "mathematical_verification",
        "identity_match",
        "content_match",
        "key_valid",
    ],
)
def test_service_rejects_failed_verification_component(
    field_name: str,
) -> None:
    arguments = {
        "receipt_id": "SVR-001",
        "verification_id": "SV-001",
        "signature_id": "SIG-001",
        "key_id": "KEY-001",
        "subject_id": "RIB-001",
        "subject_type": "RECOVERY_INTEGRITY_BUNDLE",
        "content_digest": CONTENT_DIGEST,
        "payload_digest": PAYLOAD_DIGEST,
        "public_key_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "algorithm": "ED25519",
        "signer_id": "PROCESS-LINEAGE-CLASSIFIER",
        "verifier_id": "OBSERVATORY-INSTITUTE",
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "key_valid": True,
    }
    arguments[field_name] = False

    with pytest.raises(
        SignatureVerificationReceiptError,
        match="verification component",
    ):
        SignatureVerificationReceiptService().create(**arguments)


def test_service_is_deterministic_for_same_inputs() -> None:
    first = make_receipt()
    second = make_receipt()

    assert first == second


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False