from datetime import datetime, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from models import (
    DetachedSignature,
    PublicKeyMaterial,
    RecoveryIntegrityBundle,
    RegistryVersionRecord,
    TrustedKeyRegistrySnapshot,
)
from services.canonical_signed_payload import (
    CanonicalSignedPayloadService,
)
from services.historical_signature_verification import (
    HistoricalSignatureVerificationError,
    HistoricalSignatureVerificationService,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)
from services.trusted_key_registry_snapshot_hasher import (
    TrustedKeyRegistrySnapshotHasher,
)


SIGNED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 15, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)

RECEIPT_DIGEST = "sha256:" + ("1" * 64)
AUDIT_DIGEST = "sha256:" + ("2" * 64)
MANIFEST_DIGEST = "sha256:" + ("3" * 64)
VERIFICATION_DIGEST = "sha256:" + ("4" * 64)
POLICY_DIGEST = "sha256:" + ("5" * 64)
TRUST_DIGEST = "sha256:" + ("6" * 64)
ADMISSION_RECEIPT_DIGEST = "sha256:" + ("7" * 64)
REMOVAL_RECEIPT_DIGEST = "sha256:" + ("8" * 64)


def make_bundle() -> RecoveryIntegrityBundle:
    return RecoveryIntegrityBundle(
        bundle_id="RIB-001",
        subject_id="RECOVERY-001",
        original_decision_id="RD-001",
        reconciliation_receipt_id="RCP-001",
        reconciliation_receipt_digest=RECEIPT_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_DIGEST,
        replay_manifest_id="RIM-001",
        replay_manifest_digest=MANIFEST_DIGEST,
        verification_receipt_id="RVR-001",
        verification_receipt_digest=VERIFICATION_DIGEST,
        policy_binding_id="PVB-001",
        policy_digest=POLICY_DIGEST,
        trust_provenance_ids=("TSP-001",),
        trust_digests=(TRUST_DIGEST,),
        created_at=SIGNED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_fixture():
    bundle = make_bundle()
    payload_service = CanonicalSignedPayloadService()
    payload = payload_service.generate(bundle)
    payload_digest = payload_service.digest(bundle)

    private_key = Ed25519PrivateKey.generate()
    public_key_hex = private_key.public_key().public_bytes_raw().hex()
    public_key_value = f"ed25519:{public_key_hex}"
    fingerprint = PublicKeyFingerprintService().generate(
        public_key_value
    )

    material = PublicKeyMaterial(
        material_id="PKM-001",
        key_id="KEY-001",
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        algorithm="ED25519",
        encoding="HEX",
        public_key_value=public_key_value,
        public_key_fingerprint=fingerprint,
        created_at=datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        valid_from=datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        valid_until=VALID_UNTIL,
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    signature = DetachedSignature(
        signature_id="SIG-001",
        key_id="KEY-001",
        subject_id="RIB-001",
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=payload_digest,
        algorithm="ED25519",
        signature_value=(
            "ed25519:" + private_key.sign(payload).hex()
        ),
        signed_at=SIGNED_AT,
        signer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )

    snapshot_100 = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-100",
        registry_id="TKR-001",
        registry_version="1.0.0",
        materials=(material,),
        captured_at=SIGNED_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    snapshot_110 = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-110",
        registry_id="TKR-001",
        registry_version="1.1.0",
        materials=(material,),
        captured_at=datetime(
            2026,
            7,
            15,
            14,
            0,
            tzinfo=timezone.utc,
        ),
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    snapshot_120 = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-120",
        registry_id="TKR-001",
        registry_version="1.2.0",
        materials=(
            PublicKeyMaterial(
                material_id="PKM-002",
                key_id="KEY-002",
                owner_id="PROCESS-LINEAGE-CLASSIFIER",
                algorithm="ED25519",
                encoding="HEX",
                public_key_value="ed25519:" + ("a" * 64),
                public_key_fingerprint=(
                    PublicKeyFingerprintService().generate(
                        "ed25519:" + ("a" * 64)
                    )
                ),
                created_at=datetime(
                    2026,
                    7,
                    15,
                    12,
                    0,
                    tzinfo=timezone.utc,
                ),
                valid_from=datetime(
                    2026,
                    7,
                    15,
                    12,
                    0,
                    tzinfo=timezone.utc,
                ),
                valid_until=VALID_UNTIL,
                issuer_id="OBSERVATORY-INSTITUTE",
                revoked=False,
                execution_requested=False,
                side_effects_permitted=False,
            ),
        ),
        captured_at=datetime(
            2026,
            7,
            15,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    hasher = TrustedKeyRegistrySnapshotHasher()

    record_110 = RegistryVersionRecord(
        record_id="RVR-110",
        registry_id="TKR-001",
        registry_version="1.1.0",
        previous_registry_version="1.0.0",
        snapshot_id=snapshot_110.snapshot_id,
        snapshot_digest=hasher.hash(snapshot_110),
        previous_snapshot_id=snapshot_100.snapshot_id,
        previous_snapshot_digest=hasher.hash(snapshot_100),
        transition_type="ADMISSION",
        transition_receipt_id="TKAR-001",
        transition_receipt_digest=ADMISSION_RECEIPT_DIGEST,
        recorded_at=snapshot_110.captured_at,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    record_120 = RegistryVersionRecord(
        record_id="RVR-120",
        registry_id="TKR-001",
        registry_version="1.2.0",
        previous_registry_version="1.1.0",
        snapshot_id=snapshot_120.snapshot_id,
        snapshot_digest=hasher.hash(snapshot_120),
        previous_snapshot_id=snapshot_110.snapshot_id,
        previous_snapshot_digest=hasher.hash(snapshot_110),
        transition_type="REMOVAL",
        transition_receipt_id="TKRR-001",
        transition_receipt_digest=REMOVAL_RECEIPT_DIGEST,
        recorded_at=snapshot_120.captured_at,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    return {
        "bundle": bundle,
        "signature": signature,
        "material": material,
        "snapshots": (
            snapshot_100,
            snapshot_110,
            snapshot_120,
        ),
        "records": (
            record_110,
            record_120,
        ),
    }


def verify(
    fixture: dict,
    *,
    signing_registry_version: str = "1.0.0",
    verification_registry_version: str = "1.2.0",
):
    return HistoricalSignatureVerificationService().verify(
        bundle=fixture["bundle"],
        signature=fixture["signature"],
        registry_id="TKR-001",
        signing_registry_version=signing_registry_version,
        verification_registry_version=verification_registry_version,
        snapshots=fixture["snapshots"],
        version_records=fixture["records"],
        receipt_id="HSVR-001",
        verification_id="HSV-001",
        verifier_id="OBSERVATORY-INSTITUTE",
        verified_at=VERIFIED_AT,
    )


def test_service_verifies_signature_against_historical_trust_state() -> None:
    fixture = make_fixture()

    receipt = verify(fixture)

    assert receipt.verified is True
    assert receipt.key_id == "KEY-001"
    assert receipt.subject_id == "RIB-001"
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_key_removed_at_verification_time_does_not_erase_historical_validity() -> None:
    fixture = make_fixture()

    receipt = verify(fixture)

    assert receipt.verified is True


def test_service_rejects_key_absent_at_signing_time() -> None:
    fixture = make_fixture()

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="absent from signing-time registry",
    ):
        verify(
            fixture,
            signing_registry_version="1.2.0",
        )


def test_service_rejects_unknown_signing_registry_version() -> None:
    fixture = make_fixture()

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="signing registry version",
    ):
        verify(
            fixture,
            signing_registry_version="9.9.9",
        )


def test_service_rejects_unknown_verification_registry_version() -> None:
    fixture = make_fixture()

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="verification registry version",
    ):
        verify(
            fixture,
            verification_registry_version="9.9.9",
        )


def test_service_rejects_modified_bundle() -> None:
    fixture = make_fixture()
    object.__setattr__(
        fixture["bundle"],
        "subject_id",
        "RECOVERY-999",
    )

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="content digest",
    ):
        verify(fixture)


def test_service_rejects_modified_signature() -> None:
    fixture = make_fixture()
    signature = fixture["signature"]
    encoded = signature.signature_value.removeprefix(
        "ed25519:"
    )
    replacement = (
        "0" if encoded[0] != "0" else "1"
    ) + encoded[1:]
    object.__setattr__(
        signature,
        "signature_value",
        f"ed25519:{replacement}",
    )

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="mathematical verification",
    ):
        verify(fixture)


def test_service_rejects_subject_identity_mismatch() -> None:
    fixture = make_fixture()
    object.__setattr__(
        fixture["signature"],
        "subject_id",
        "RIB-999",
    )

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="subject identity",
    ):
        verify(fixture)


def test_service_rejects_verification_before_signature() -> None:
    fixture = make_fixture()

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="before signature creation",
    ):
        HistoricalSignatureVerificationService().verify(
            bundle=fixture["bundle"],
            signature=fixture["signature"],
            registry_id="TKR-001",
            signing_registry_version="1.0.0",
            verification_registry_version="1.2.0",
            snapshots=fixture["snapshots"],
            version_records=fixture["records"],
            receipt_id="HSVR-001",
            verification_id="HSV-001",
            verifier_id="OBSERVATORY-INSTITUTE",
            verified_at=datetime(
                2026,
                7,
                15,
                12,
                59,
                tzinfo=timezone.utc,
            ),
        )


def test_service_rejects_empty_registry_identity() -> None:
    fixture = make_fixture()

    with pytest.raises(
        HistoricalSignatureVerificationError,
        match="registry_id",
    ):
        HistoricalSignatureVerificationService().verify(
            bundle=fixture["bundle"],
            signature=fixture["signature"],
            registry_id="",
            signing_registry_version="1.0.0",
            verification_registry_version="1.2.0",
            snapshots=fixture["snapshots"],
            version_records=fixture["records"],
            receipt_id="HSVR-001",
            verification_id="HSV-001",
            verifier_id="OBSERVATORY-INSTITUTE",
            verified_at=VERIFIED_AT,
        )


def test_service_rejects_non_tuple_snapshots() -> None:
    fixture = make_fixture()

    with pytest.raises(TypeError, match="snapshots"):
        HistoricalSignatureVerificationService().verify(
            bundle=fixture["bundle"],
            signature=fixture["signature"],
            registry_id="TKR-001",
            signing_registry_version="1.0.0",
            verification_registry_version="1.2.0",
            snapshots=[],  # type: ignore[arg-type]
            version_records=fixture["records"],
            receipt_id="HSVR-001",
            verification_id="HSV-001",
            verifier_id="OBSERVATORY-INSTITUTE",
            verified_at=VERIFIED_AT,
        )


def test_service_rejects_non_tuple_version_records() -> None:
    fixture = make_fixture()

    with pytest.raises(TypeError, match="version_records"):
        HistoricalSignatureVerificationService().verify(
            bundle=fixture["bundle"],
            signature=fixture["signature"],
            registry_id="TKR-001",
            signing_registry_version="1.0.0",
            verification_registry_version="1.2.0",
            snapshots=fixture["snapshots"],
            version_records=[],  # type: ignore[arg-type]
            receipt_id="HSVR-001",
            verification_id="HSV-001",
            verifier_id="OBSERVATORY-INSTITUTE",
            verified_at=VERIFIED_AT,
        )


def test_service_is_deterministic() -> None:
    fixture = make_fixture()

    first = verify(fixture)
    second = verify(fixture)

    assert first == second


def test_service_does_not_mutate_inputs() -> None:
    fixture = make_fixture()
    original_bundle = fixture["bundle"]
    original_signature = fixture["signature"]
    original_snapshots = fixture["snapshots"]
    original_records = fixture["records"]

    verify(fixture)

    assert fixture["bundle"] == original_bundle
    assert fixture["signature"] == original_signature
    assert fixture["snapshots"] == original_snapshots
    assert fixture["records"] == original_records