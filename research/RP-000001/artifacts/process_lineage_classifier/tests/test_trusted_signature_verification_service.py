from datetime import datetime, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from models import (
    DetachedSignature,
    PublicKeyMaterial,
    RecoveryIntegrityBundle,
    SignatureVerificationReceipt,
)
from services.canonical_signed_payload import (
    CanonicalSignedPayloadService,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)
from services.trusted_key_registry import (
    TrustedKeyRegistry,
)
from services.trusted_signature_verification_service import (
    TrustedSignatureVerificationError,
    TrustedSignatureVerificationService,
)


SIGNED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
RECEIPT_DIGEST = "sha256:" + ("2" * 64)
AUDIT_DIGEST = "sha256:" + ("3" * 64)
MANIFEST_DIGEST = "sha256:" + ("4" * 64)
VERIFICATION_DIGEST = "sha256:" + ("5" * 64)
POLICY_DIGEST = "sha256:" + ("6" * 64)
TRUST_DIGEST = "sha256:" + ("7" * 64)


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


def make_fixture() -> tuple[
    RecoveryIntegrityBundle,
    DetachedSignature,
    PublicKeyMaterial,
    TrustedKeyRegistry,
]:
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
        created_at=SIGNED_AT,
        valid_from=SIGNED_AT,
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

    registry = TrustedKeyRegistry(
        expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
        expected_issuer_id="OBSERVATORY-INSTITUTE",
    )
    registry.register(material)

    return bundle, signature, material, registry


def verify(
    *,
    bundle: RecoveryIntegrityBundle,
    signature: DetachedSignature,
    registry: TrustedKeyRegistry,
    receipt_id: str = "SVR-001",
    verification_id: str = "SV-001",
    verifier_id: str = "OBSERVATORY-INSTITUTE",
    verified_at: datetime = SIGNED_AT,
) -> SignatureVerificationReceipt:
    return TrustedSignatureVerificationService().verify(
        bundle=bundle,
        signature=signature,
        registry=registry,
        receipt_id=receipt_id,
        verification_id=verification_id,
        verifier_id=verifier_id,
        verified_at=verified_at,
    )


def test_service_verifies_trusted_signature() -> None:
    bundle, signature, material, registry = make_fixture()

    receipt = verify(
        bundle=bundle,
        signature=signature,
        registry=registry,
    )

    assert isinstance(receipt, SignatureVerificationReceipt)
    assert receipt.receipt_id == "SVR-001"
    assert receipt.verification_id == "SV-001"
    assert receipt.signature_id == signature.signature_id
    assert receipt.key_id == material.key_id
    assert receipt.subject_id == bundle.bundle_id
    assert receipt.content_digest == signature.content_digest
    assert receipt.public_key_fingerprint == (
        material.public_key_fingerprint
    )
    assert receipt.mathematical_verification is True
    assert receipt.identity_match is True
    assert receipt.content_match is True
    assert receipt.key_valid is True
    assert receipt.verified is True


def test_service_rejects_non_bundle_input() -> None:
    _, signature, _, registry = make_fixture()

    with pytest.raises(TypeError, match="RecoveryIntegrityBundle"):
        verify(
            bundle="RIB-001",  # type: ignore[arg-type]
            signature=signature,
            registry=registry,
        )


def test_service_rejects_non_signature_input() -> None:
    bundle, _, _, registry = make_fixture()

    with pytest.raises(TypeError, match="DetachedSignature"):
        verify(
            bundle=bundle,
            signature="SIG-001",  # type: ignore[arg-type]
            registry=registry,
        )


def test_service_rejects_non_registry_input() -> None:
    bundle, signature, _, _ = make_fixture()

    with pytest.raises(TypeError, match="TrustedKeyRegistry"):
        verify(
            bundle=bundle,
            signature=signature,
            registry="registry",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "receipt_id",
        "verification_id",
        "verifier_id",
    ],
)
def test_service_rejects_empty_identity(
    field_name: str,
) -> None:
    bundle, signature, _, registry = make_fixture()
    arguments = {
        "bundle": bundle,
        "signature": signature,
        "registry": registry,
        "receipt_id": "SVR-001",
        "verification_id": "SV-001",
        "verifier_id": "OBSERVATORY-INSTITUTE",
    }
    arguments[field_name] = ""

    with pytest.raises(
        TrustedSignatureVerificationError,
        match=field_name,
    ):
        verify(**arguments)


def test_service_rejects_naive_verified_at() -> None:
    bundle, signature, _, registry = make_fixture()

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="timezone-aware",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
            verified_at=datetime(2026, 7, 15, 12, 0),
        )


def test_service_rejects_verification_before_signature() -> None:
    bundle, signature, _, registry = make_fixture()

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="before signature creation",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
            verified_at=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            ),
        )


def test_service_rejects_unknown_key() -> None:
    bundle, signature, _, _ = make_fixture()
    empty_registry = TrustedKeyRegistry()

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="trusted key",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=empty_registry,
        )


def test_service_rejects_subject_identity_mismatch() -> None:
    bundle, signature, _, registry = make_fixture()
    object.__setattr__(signature, "subject_id", "RIB-999")

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="subject identity",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
        )


def test_service_rejects_subject_type_mismatch() -> None:
    bundle, signature, _, registry = make_fixture()
    object.__setattr__(
        signature,
        "subject_type",
        "OTHER",
    )

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="subject type",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
        )


def test_service_rejects_content_digest_mismatch() -> None:
    bundle, signature, _, registry = make_fixture()
    object.__setattr__(
        signature,
        "content_digest",
        "sha256:" + ("9" * 64),
    )

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="content digest",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
        )


def test_service_rejects_modified_bundle() -> None:
    bundle, signature, _, registry = make_fixture()
    object.__setattr__(bundle, "subject_id", "RECOVERY-999")

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="content digest",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
        )


def test_service_rejects_modified_signature() -> None:
    bundle, signature, _, registry = make_fixture()
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
        TrustedSignatureVerificationError,
        match="mathematical verification",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
        )


def test_service_rejects_revoked_registry_material() -> None:
    bundle, signature, material, registry = make_fixture()
    object.__setattr__(material, "revoked", True)

    with pytest.raises(
        TrustedSignatureVerificationError,
        match="revoked",
    ):
        verify(
            bundle=bundle,
            signature=signature,
            registry=registry,
        )


def test_service_is_deterministic_for_same_inputs() -> None:
    bundle, signature, _, registry = make_fixture()

    first = verify(
        bundle=bundle,
        signature=signature,
        registry=registry,
    )
    second = verify(
        bundle=bundle,
        signature=signature,
        registry=registry,
    )

    assert first == second


def test_service_does_not_mutate_inputs() -> None:
    bundle, signature, material, registry = make_fixture()
    original_bundle = bundle
    original_signature = signature
    original_material = material

    verify(
        bundle=bundle,
        signature=signature,
        registry=registry,
    )

    assert bundle == original_bundle
    assert signature == original_signature
    assert material == original_material


def test_service_preserves_observer_only_boundary() -> None:
    bundle, signature, material, registry = make_fixture()

    receipt = verify(
        bundle=bundle,
        signature=signature,
        registry=registry,
    )

    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False
    assert signature.execution_requested is False
    assert signature.side_effects_permitted is False
    assert material.execution_requested is False
    assert material.side_effects_permitted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False