from datetime import datetime, timezone

import pytest

from models import (
    DetachedSignature,
    RecoveryIntegrityBundle,
    SignatureVerification,
    SignedIntegrityBundle,
    SigningKeyIdentity,
)
from services.signed_integrity_bundle_validator import (
    SignedIntegrityBundleError,
    SignedIntegrityBundleValidator,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
SIGNED_AT = datetime(2026, 7, 15, 12, 0, 1, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 12, 0, 2, tzinfo=timezone.utc)

BUNDLE_DIGEST = "sha256:" + ("1" * 64)
RECONCILIATION_RECEIPT_DIGEST = "sha256:" + ("2" * 64)
AUDIT_ROOT_DIGEST = "sha256:" + ("3" * 64)
REPLAY_MANIFEST_DIGEST = "sha256:" + ("4" * 64)
VERIFICATION_RECEIPT_DIGEST = "sha256:" + ("5" * 64)
POLICY_DIGEST = "sha256:" + ("6" * 64)
TRUST_DIGEST = "sha256:" + ("7" * 64)
KEY_FINGERPRINT = "sha256:" + ("8" * 64)
SIGNATURE_VALUE = "ed25519:" + ("a" * 128)


def make_bundle() -> RecoveryIntegrityBundle:
    return RecoveryIntegrityBundle(
        bundle_id="RIB-001",
        subject_id="RECOVERY-001",
        original_decision_id="RD-001",
        reconciliation_receipt_id="RCP-001",
        reconciliation_receipt_digest=RECONCILIATION_RECEIPT_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        verification_receipt_id="RVR-001",
        verification_receipt_digest=VERIFICATION_RECEIPT_DIGEST,
        policy_binding_id="PVB-001",
        policy_digest=POLICY_DIGEST,
        trust_provenance_ids=("TSP-001",),
        trust_digests=(TRUST_DIGEST,),
        created_at=CREATED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_key(
    *,
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> SigningKeyIdentity:
    return SigningKeyIdentity(
        key_id=key_id,
        owner_id=owner_id,
        algorithm="ED25519",
        public_key_fingerprint=KEY_FINGERPRINT,
        created_at=CREATED_AT,
        valid_from=CREATED_AT,
        valid_until=datetime(
            2027,
            7,
            15,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_signature(
    *,
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    subject_id: str = "RIB-001",
    content_digest: str = BUNDLE_DIGEST,
    signer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> DetachedSignature:
    return DetachedSignature(
        signature_id=signature_id,
        key_id=key_id,
        subject_id=subject_id,
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=content_digest,
        algorithm="ED25519",
        signature_value=SIGNATURE_VALUE,
        signed_at=SIGNED_AT,
        signer_id=signer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_verification(
    *,
    verification_id: str = "SV-001",
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    subject_id: str = "RIB-001",
    content_digest: str = BUNDLE_DIGEST,
    signer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    key_owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    verified: bool = True,
) -> SignatureVerification:
    return SignatureVerification(
        verification_id=verification_id,
        signature_id=signature_id,
        key_id=key_id,
        subject_id=subject_id,
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=content_digest,
        signer_id=signer_id,
        key_owner_id=key_owner_id,
        algorithm="ED25519",
        signature_verified=verified,
        key_valid=verified,
        identity_match=verified,
        content_match=verified,
        verified=verified,
        verified_at=VERIFIED_AT,
        verifier_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_signed_bundle(
    *,
    signed_bundle_id: str = "SIB-001",
    bundle: RecoveryIntegrityBundle | None = None,
    bundle_digest: str = BUNDLE_DIGEST,
    signature: DetachedSignature | None = None,
    key: SigningKeyIdentity | None = None,
    verification: SignatureVerification | None = None,
    created_at: datetime = VERIFIED_AT,
    issuer_id: str = "OBSERVATORY-INSTITUTE",
) -> SignedIntegrityBundle:
    bundle_value = make_bundle() if bundle is None else bundle
    signature_value = make_signature() if signature is None else signature
    key_value = make_key() if key is None else key
    verification_value = (
        make_verification()
        if verification is None
        else verification
    )

    return SignedIntegrityBundle(
        signed_bundle_id=signed_bundle_id,
        bundle=bundle_value,
        bundle_digest=bundle_digest,
        signature=signature_value,
        signing_key=key_value,
        verification=verification_value,
        created_at=created_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_signed_bundle() -> None:
    signed_bundle = make_signed_bundle()

    assert SignedIntegrityBundleValidator().validate(
        signed_bundle
    ) is True


def test_signed_bundle_is_immutable() -> None:
    signed_bundle = make_signed_bundle()

    with pytest.raises((AttributeError, TypeError)):
        signed_bundle.bundle_digest = POLICY_DIGEST  # type: ignore[misc]


def test_signed_bundle_rejects_empty_identity() -> None:
    with pytest.raises(ValueError, match="signed_bundle_id"):
        make_signed_bundle(signed_bundle_id="")


def test_signed_bundle_rejects_invalid_bundle_digest() -> None:
    with pytest.raises(ValueError, match="bundle_digest"):
        make_signed_bundle(bundle_digest="sha256:abc")


def test_signed_bundle_rejects_non_bundle_input() -> None:
    with pytest.raises(TypeError, match="RecoveryIntegrityBundle"):
        SignedIntegrityBundle(
            signed_bundle_id="SIB-001",
            bundle="RIB-001",  # type: ignore[arg-type]
            bundle_digest=BUNDLE_DIGEST,
            signature=make_signature(),
            signing_key=make_key(),
            verification=make_verification(),
            created_at=VERIFIED_AT,
            issuer_id="OBSERVATORY-INSTITUTE",
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_signed_bundle_rejects_non_signature_input() -> None:
    with pytest.raises(TypeError, match="DetachedSignature"):
        SignedIntegrityBundle(
            signed_bundle_id="SIB-001",
            bundle=make_bundle(),
            bundle_digest=BUNDLE_DIGEST,
            signature="SIG-001",  # type: ignore[arg-type]
            signing_key=make_key(),
            verification=make_verification(),
            created_at=VERIFIED_AT,
            issuer_id="OBSERVATORY-INSTITUTE",
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_signed_bundle_rejects_non_key_input() -> None:
    with pytest.raises(TypeError, match="SigningKeyIdentity"):
        SignedIntegrityBundle(
            signed_bundle_id="SIB-001",
            bundle=make_bundle(),
            bundle_digest=BUNDLE_DIGEST,
            signature=make_signature(),
            signing_key="KEY-001",  # type: ignore[arg-type]
            verification=make_verification(),
            created_at=VERIFIED_AT,
            issuer_id="OBSERVATORY-INSTITUTE",
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_signed_bundle_rejects_non_verification_input() -> None:
    with pytest.raises(TypeError, match="SignatureVerification"):
        SignedIntegrityBundle(
            signed_bundle_id="SIB-001",
            bundle=make_bundle(),
            bundle_digest=BUNDLE_DIGEST,
            signature=make_signature(),
            signing_key=make_key(),
            verification="SV-001",  # type: ignore[arg-type]
            created_at=VERIFIED_AT,
            issuer_id="OBSERVATORY-INSTITUTE",
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_signed_bundle_rejects_unverified_verification() -> None:
    with pytest.raises(ValueError, match="verified"):
        make_signed_bundle(
            verification=make_verification(verified=False)
        )


def test_signed_bundle_rejects_naive_created_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_signed_bundle(
            created_at=datetime(2026, 7, 15, 12, 0)
        )


def test_signed_bundle_rejects_creation_before_verification() -> None:
    with pytest.raises(ValueError, match="before verification"):
        make_signed_bundle(created_at=SIGNED_AT)


def test_signed_bundle_rejects_empty_issuer_id() -> None:
    with pytest.raises(ValueError, match="issuer_id"):
        make_signed_bundle(issuer_id="")


def test_validator_rejects_non_signed_bundle_input() -> None:
    with pytest.raises(TypeError, match="SignedIntegrityBundle"):
        SignedIntegrityBundleValidator().validate(
            "SIB-001"  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    (
        "signature",
        "key",
        "verification",
        "error_match",
    ),
    [
        (
            make_signature(subject_id="RIB-999"),
            make_key(),
            make_verification(),
            "signature subject identity",
        ),
        (
            make_signature(content_digest=POLICY_DIGEST),
            make_key(),
            make_verification(),
            "signature content digest",
        ),
        (
            make_signature(key_id="KEY-999"),
            make_key(),
            make_verification(),
            "signature key identity",
        ),
        (
            make_signature(signer_id="OTHER-SIGNER"),
            make_key(),
            make_verification(),
            "signature signer identity",
        ),
        (
            make_signature(),
            make_key(key_id="KEY-999"),
            make_verification(),
            "signature key identity",
        ),
        (
            make_signature(),
            make_key(owner_id="OTHER-OWNER"),
            make_verification(),
            "signature signer identity",
        ),
        (
            make_signature(),
            make_key(),
            make_verification(signature_id="SIG-999"),
            "verification signature identity",
        ),
        (
            make_signature(),
            make_key(),
            make_verification(key_id="KEY-999"),
            "verification key identity",
        ),
        (
            make_signature(),
            make_key(),
            make_verification(subject_id="RIB-999"),
            "verification subject identity",
        ),
        (
            make_signature(),
            make_key(),
            make_verification(content_digest=POLICY_DIGEST),
            "verification content digest",
        ),
        (
            make_signature(),
            make_key(),
            make_verification(signer_id="OTHER-SIGNER"),
            "verification signer identity",
        ),
        (
            make_signature(),
            make_key(),
            make_verification(key_owner_id="OTHER-OWNER"),
            "verification key owner",
        ),
    ],
)
def test_validator_rejects_reference_mismatch(
    signature: DetachedSignature,
    key: SigningKeyIdentity,
    verification: SignatureVerification,
    error_match: str,
) -> None:
    signed_bundle = make_signed_bundle(
        signature=signature,
        key=key,
        verification=verification,
    )

    with pytest.raises(
        SignedIntegrityBundleError,
        match=error_match,
    ):
        SignedIntegrityBundleValidator().validate(signed_bundle)


def test_validator_does_not_mutate_signed_bundle() -> None:
    signed_bundle = make_signed_bundle()
    original = signed_bundle

    SignedIntegrityBundleValidator().validate(signed_bundle)

    assert signed_bundle == original


def test_signed_bundle_preserves_observer_only_boundary() -> None:
    signed_bundle = make_signed_bundle()

    assert signed_bundle.execution_requested is False
    assert signed_bundle.side_effects_permitted is False