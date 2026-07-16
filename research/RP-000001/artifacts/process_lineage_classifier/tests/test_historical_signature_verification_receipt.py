from datetime import datetime, timezone

import pytest

from models import HistoricalSignatureVerificationReceipt
from services.historical_signature_verification_receipt_service import (
    HistoricalSignatureVerificationReceiptError,
    HistoricalSignatureVerificationReceiptService,
)


SIGNED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 15, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
PAYLOAD_DIGEST = "sha256:" + ("2" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("3" * 64)
SIGNING_SNAPSHOT_DIGEST = "sha256:" + ("4" * 64)
VERIFICATION_SNAPSHOT_DIGEST = "sha256:" + ("5" * 64)


def make_receipt() -> HistoricalSignatureVerificationReceipt:
    return HistoricalSignatureVerificationReceiptService().create(
        receipt_id="HSVR-001",
        verification_id="HSV-001",
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
        registry_id="TKR-001",
        signing_registry_version="1.0.0",
        signing_snapshot_id="TKRS-100",
        signing_snapshot_digest=SIGNING_SNAPSHOT_DIGEST,
        verification_registry_version="1.2.0",
        verification_snapshot_id="TKRS-120",
        verification_snapshot_digest=VERIFICATION_SNAPSHOT_DIGEST,
        signed_at=SIGNED_AT,
        verified_at=VERIFIED_AT,
        mathematical_verification=True,
        identity_match=True,
        content_match=True,
        signing_time_key_present=True,
        verification_time_key_present=False,
        key_valid_at_signing=True,
    )


def test_service_creates_historical_verification_receipt() -> None:
    receipt = make_receipt()

    assert isinstance(
        receipt,
        HistoricalSignatureVerificationReceipt,
    )
    assert receipt.receipt_id == "HSVR-001"
    assert receipt.verification_id == "HSV-001"
    assert receipt.signature_id == "SIG-001"
    assert receipt.key_id == "KEY-001"
    assert receipt.subject_id == "RIB-001"
    assert receipt.registry_id == "TKR-001"
    assert receipt.signing_registry_version == "1.0.0"
    assert receipt.signing_snapshot_id == "TKRS-100"
    assert receipt.signing_snapshot_digest == SIGNING_SNAPSHOT_DIGEST
    assert receipt.verification_registry_version == "1.2.0"
    assert receipt.verification_snapshot_id == "TKRS-120"
    assert (
        receipt.verification_snapshot_digest
        == VERIFICATION_SNAPSHOT_DIGEST
    )
    assert receipt.signed_at == SIGNED_AT
    assert receipt.verified_at == VERIFIED_AT
    assert receipt.mathematical_verification is True
    assert receipt.identity_match is True
    assert receipt.content_match is True
    assert receipt.signing_time_key_present is True
    assert receipt.verification_time_key_present is False
    assert receipt.key_valid_at_signing is True
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
        "registry_id",
        "signing_registry_version",
        "signing_snapshot_id",
        "verification_registry_version",
        "verification_snapshot_id",
    ],
)
def test_service_rejects_empty_identity(
    field_name: str,
) -> None:
    arguments = {
        "receipt_id": "HSVR-001",
        "verification_id": "HSV-001",
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
        "registry_id": "TKR-001",
        "signing_registry_version": "1.0.0",
        "signing_snapshot_id": "TKRS-100",
        "signing_snapshot_digest": SIGNING_SNAPSHOT_DIGEST,
        "verification_registry_version": "1.2.0",
        "verification_snapshot_id": "TKRS-120",
        "verification_snapshot_digest": VERIFICATION_SNAPSHOT_DIGEST,
        "signed_at": SIGNED_AT,
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "signing_time_key_present": True,
        "verification_time_key_present": False,
        "key_valid_at_signing": True,
    }
    arguments[field_name] = ""

    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match=field_name,
    ):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("content_digest", "md5:invalid"),
        ("payload_digest", "sha256:abc"),
        (
            "public_key_fingerprint",
            "sha256:" + ("z" * 64),
        ),
        (
            "signing_snapshot_digest",
            "sha256:" + ("A" * 64),
        ),
        (
            "verification_snapshot_digest",
            "sha256:" + ("x" * 64),
        ),
    ],
)
def test_service_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "receipt_id": "HSVR-001",
        "verification_id": "HSV-001",
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
        "registry_id": "TKR-001",
        "signing_registry_version": "1.0.0",
        "signing_snapshot_id": "TKRS-100",
        "signing_snapshot_digest": SIGNING_SNAPSHOT_DIGEST,
        "verification_registry_version": "1.2.0",
        "verification_snapshot_id": "TKRS-120",
        "verification_snapshot_digest": VERIFICATION_SNAPSHOT_DIGEST,
        "signed_at": SIGNED_AT,
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "signing_time_key_present": True,
        "verification_time_key_present": False,
        "key_valid_at_signing": True,
    }
    arguments[field_name] = value

    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match=field_name,
    ):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


def test_service_rejects_unsupported_algorithm() -> None:
    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match="algorithm",
    ):
        arguments = make_arguments()
        arguments["algorithm"] = "RSA"
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


def make_arguments() -> dict[str, object]:
    return {
        "receipt_id": "HSVR-001",
        "verification_id": "HSV-001",
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
        "registry_id": "TKR-001",
        "signing_registry_version": "1.0.0",
        "signing_snapshot_id": "TKRS-100",
        "signing_snapshot_digest": SIGNING_SNAPSHOT_DIGEST,
        "verification_registry_version": "1.2.0",
        "verification_snapshot_id": "TKRS-120",
        "verification_snapshot_digest": VERIFICATION_SNAPSHOT_DIGEST,
        "signed_at": SIGNED_AT,
        "verified_at": VERIFIED_AT,
        "mathematical_verification": True,
        "identity_match": True,
        "content_match": True,
        "signing_time_key_present": True,
        "verification_time_key_present": False,
        "key_valid_at_signing": True,
    }


def test_service_rejects_naive_signed_at() -> None:
    arguments = make_arguments()
    arguments["signed_at"] = datetime(2026, 7, 15, 13, 0)

    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match="signed_at.*timezone-aware",
    ):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


def test_service_rejects_naive_verified_at() -> None:
    arguments = make_arguments()
    arguments["verified_at"] = datetime(2026, 7, 15, 15, 0)

    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match="verified_at.*timezone-aware",
    ):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


def test_service_rejects_verification_before_signature() -> None:
    arguments = make_arguments()
    arguments["verified_at"] = datetime(
        2026,
        7,
        15,
        12,
        59,
        tzinfo=timezone.utc,
    )

    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match="before signature creation",
    ):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "mathematical_verification",
        "identity_match",
        "content_match",
        "signing_time_key_present",
        "verification_time_key_present",
        "key_valid_at_signing",
    ],
)
def test_service_rejects_non_boolean_component(
    field_name: str,
) -> None:
    arguments = make_arguments()
    arguments[field_name] = "true"

    with pytest.raises(TypeError, match=field_name):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "mathematical_verification",
        "identity_match",
        "content_match",
        "signing_time_key_present",
        "key_valid_at_signing",
    ],
)
def test_service_rejects_failed_required_component(
    field_name: str,
) -> None:
    arguments = make_arguments()
    arguments[field_name] = False

    with pytest.raises(
        HistoricalSignatureVerificationReceiptError,
        match="required verification component",
    ):
        HistoricalSignatureVerificationReceiptService().create(
            **arguments
        )


def test_verification_time_key_presence_may_be_false() -> None:
    receipt = make_receipt()

    assert receipt.verification_time_key_present is False
    assert receipt.verified is True


def test_service_is_deterministic_for_same_inputs() -> None:
    assert make_receipt() == make_receipt()


def test_receipt_preserves_non_retroactive_boundary() -> None:
    receipt = make_receipt()

    assert receipt.signing_time_key_present is True
    assert receipt.verification_time_key_present is False
    assert receipt.verified is True


def test_receipt_preserves_observer_only_boundary() -> None:
    receipt = make_receipt()

    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False