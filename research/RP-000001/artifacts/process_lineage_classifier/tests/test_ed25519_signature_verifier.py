from datetime import datetime, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from models import (
    DetachedSignature,
    PublicKeyMaterial,
)
from services.ed25519_signature_verifier import (
    Ed25519SignatureVerificationError,
    Ed25519SignatureVerifier,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)


SIGNED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)

MESSAGE = b"recovery-integrity-bundle:RIB-001"
CONTENT_DIGEST = "sha256:" + ("1" * 64)


def make_material_and_signature(
    *,
    message: bytes = MESSAGE,
) -> tuple[PublicKeyMaterial, DetachedSignature]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    public_key_hex = public_key.public_bytes_raw().hex()
    public_key_value = f"ed25519:{public_key_hex}"
    fingerprint = PublicKeyFingerprintService().generate(
        public_key_value
    )

    signature_hex = private_key.sign(message).hex()

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
        content_digest=CONTENT_DIGEST,
        algorithm="ED25519",
        signature_value=f"ed25519:{signature_hex}",
        signed_at=SIGNED_AT,
        signer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )

    return material, signature


def test_verifier_accepts_valid_signature() -> None:
    material, signature = make_material_and_signature()

    assert Ed25519SignatureVerifier().verify(
        message=MESSAGE,
        signature=signature,
        public_key_material=material,
    ) is True


def test_verifier_rejects_non_bytes_message() -> None:
    material, signature = make_material_and_signature()

    with pytest.raises(TypeError, match="bytes"):
        Ed25519SignatureVerifier().verify(
            message="message",  # type: ignore[arg-type]
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_empty_message() -> None:
    material, signature = make_material_and_signature()

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="must not be empty",
    ):
        Ed25519SignatureVerifier().verify(
            message=b"",
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_non_signature_input() -> None:
    material, _ = make_material_and_signature()

    with pytest.raises(TypeError, match="DetachedSignature"):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature="SIG-001",  # type: ignore[arg-type]
            public_key_material=material,
        )


def test_verifier_rejects_non_material_input() -> None:
    _, signature = make_material_and_signature()

    with pytest.raises(TypeError, match="PublicKeyMaterial"):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material="PKM-001",  # type: ignore[arg-type]
        )


def test_verifier_rejects_key_identity_mismatch() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(material, "key_id", "KEY-999")

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="key identity",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_signer_owner_mismatch() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(material, "owner_id", "OTHER-OWNER")

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="signer identity",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_algorithm_mismatch() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(material, "algorithm", "OTHER")

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="algorithm",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_revoked_public_key_material() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(material, "revoked", True)

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="revoked",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_signature_before_key_validity() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(
        material,
        "valid_from",
        datetime(
            2026,
            7,
            15,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="before key validity",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_signature_after_key_validity() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(
        material,
        "valid_until",
        datetime(
            2026,
            7,
            15,
            11,
            59,
            59,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="after key validity",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_fingerprint_mismatch() -> None:
    material, signature = make_material_and_signature()
    object.__setattr__(
        material,
        "public_key_fingerprint",
        "sha256:" + ("9" * 64),
    )

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="fingerprint",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_modified_message() -> None:
    material, signature = make_material_and_signature()

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="mathematical verification failed",
    ):
        Ed25519SignatureVerifier().verify(
            message=b"modified-message",
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_modified_signature() -> None:
    material, signature = make_material_and_signature()
    original_hex = signature.signature_value.removeprefix(
        "ed25519:"
    )
    replacement = (
        "0" if original_hex[0] != "0" else "1"
    ) + original_hex[1:]
    object.__setattr__(
        signature,
        "signature_value",
        f"ed25519:{replacement}",
    )

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="mathematical verification failed",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_rejects_modified_public_key() -> None:
    material, signature = make_material_and_signature()
    original_hex = material.public_key_value.removeprefix(
        "ed25519:"
    )
    replacement = (
        "0" if original_hex[0] != "0" else "1"
    ) + original_hex[1:]
    object.__setattr__(
        material,
        "public_key_value",
        f"ed25519:{replacement}",
    )
    object.__setattr__(
        material,
        "public_key_fingerprint",
        PublicKeyFingerprintService().generate(
            material.public_key_value
        ),
    )

    with pytest.raises(
        Ed25519SignatureVerificationError,
        match="mathematical verification failed",
    ):
        Ed25519SignatureVerifier().verify(
            message=MESSAGE,
            signature=signature,
            public_key_material=material,
        )


def test_verifier_does_not_mutate_inputs() -> None:
    material, signature = make_material_and_signature()
    original_material = material
    original_signature = signature

    Ed25519SignatureVerifier().verify(
        message=MESSAGE,
        signature=signature,
        public_key_material=material,
    )

    assert material == original_material
    assert signature == original_signature


def test_inputs_preserve_observer_only_boundary() -> None:
    material, signature = make_material_and_signature()

    assert material.execution_requested is False
    assert material.side_effects_permitted is False
    assert signature.execution_requested is False
    assert signature.side_effects_permitted is False