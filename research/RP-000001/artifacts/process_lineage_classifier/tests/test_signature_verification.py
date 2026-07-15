from datetime import datetime, timezone

import pytest

from models import DetachedSignature, SignatureVerification, SigningKeyIdentity
from services.signature_verification_service import (
    SignatureVerificationError,
    SignatureVerificationService,
)

SIGNED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 12, 0, 1, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)
CONTENT_DIGEST = "sha256:" + ("1" * 64)
KEY_FINGERPRINT = "sha256:" + ("2" * 64)
SIGNATURE_VALUE = "ed25519:" + ("a" * 128)


def make_key(
    *,
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    algorithm: str = "ED25519",
    public_key_fingerprint: str = KEY_FINGERPRINT,
    created_at: datetime = SIGNED_AT,
    valid_from: datetime = SIGNED_AT,
    valid_until: datetime = VALID_UNTIL,
    issuer_id: str = "OBSERVATORY-INSTITUTE",
    revoked: bool = False,
) -> SigningKeyIdentity:
    return SigningKeyIdentity(
        key_id=key_id,
        owner_id=owner_id,
        algorithm=algorithm,
        public_key_fingerprint=public_key_fingerprint,
        created_at=created_at,
        valid_from=valid_from,
        valid_until=valid_until,
        issuer_id=issuer_id,
        revoked=revoked,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_signature(
    *,
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    subject_id: str = "RIB-001",
    subject_type: str = "RECOVERY_INTEGRITY_BUNDLE",
    content_digest: str = CONTENT_DIGEST,
    algorithm: str = "ED25519",
    signature_value: str = SIGNATURE_VALUE,
    signed_at: datetime = SIGNED_AT,
    signer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> DetachedSignature:
    return DetachedSignature(
        signature_id=signature_id,
        key_id=key_id,
        subject_id=subject_id,
        subject_type=subject_type,
        content_digest=content_digest,
        algorithm=algorithm,
        signature_value=signature_value,
        signed_at=signed_at,
        signer_id=signer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def verify(
    *,
    signature: DetachedSignature | None = None,
    key: SigningKeyIdentity | None = None,
    expected_subject_id: str = "RIB-001",
    expected_subject_type: str = "RECOVERY_INTEGRITY_BUNDLE",
    expected_content_digest: str = CONTENT_DIGEST,
    verified_at: datetime = VERIFIED_AT,
    verification_id: str = "SV-001",
    verifier_id: str = "OBSERVATORY-INSTITUTE",
) -> SignatureVerification:
    return SignatureVerificationService().verify(
        verification_id=verification_id,
        signature=make_signature() if signature is None else signature,
        key=make_key() if key is None else key,
        expected_subject_id=expected_subject_id,
        expected_subject_type=expected_subject_type,
        expected_content_digest=expected_content_digest,
        verified_at=verified_at,
        verifier_id=verifier_id,
    )


def test_service_returns_verified_result() -> None:
    result = verify()
    assert isinstance(result, SignatureVerification)
    assert result.verification_id == "SV-001"
    assert result.signature_id == "SIG-001"
    assert result.key_id == "KEY-001"
    assert result.subject_id == "RIB-001"
    assert result.subject_type == "RECOVERY_INTEGRITY_BUNDLE"
    assert result.content_digest == CONTENT_DIGEST
    assert result.signer_id == "PROCESS-LINEAGE-CLASSIFIER"
    assert result.key_owner_id == "PROCESS-LINEAGE-CLASSIFIER"
    assert result.algorithm == "ED25519"
    assert result.signature_verified is True
    assert result.key_valid is True
    assert result.identity_match is True
    assert result.content_match is True
    assert result.verified is True
    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_service_rejects_non_signature_input() -> None:
    with pytest.raises(TypeError, match="DetachedSignature"):
        SignatureVerificationService().verify(
            verification_id="SV-001",
            signature="SIG-001",  # type: ignore[arg-type]
            key=make_key(),
            expected_subject_id="RIB-001",
            expected_subject_type="RECOVERY_INTEGRITY_BUNDLE",
            expected_content_digest=CONTENT_DIGEST,
            verified_at=VERIFIED_AT,
            verifier_id="OBSERVATORY-INSTITUTE",
        )


def test_service_rejects_non_key_input() -> None:
    with pytest.raises(TypeError, match="SigningKeyIdentity"):
        SignatureVerificationService().verify(
            verification_id="SV-001",
            signature=make_signature(),
            key="KEY-001",  # type: ignore[arg-type]
            expected_subject_id="RIB-001",
            expected_subject_type="RECOVERY_INTEGRITY_BUNDLE",
            expected_content_digest=CONTENT_DIGEST,
            verified_at=VERIFIED_AT,
            verifier_id="OBSERVATORY-INSTITUTE",
        )


def test_service_rejects_empty_verification_id() -> None:
    with pytest.raises(SignatureVerificationError, match="verification_id"):
        verify(verification_id="")


def test_service_rejects_empty_verifier_id() -> None:
    with pytest.raises(SignatureVerificationError, match="verifier_id"):
        verify(verifier_id="")


def test_service_rejects_key_identity_mismatch() -> None:
    with pytest.raises(SignatureVerificationError, match="key identity"):
        verify(
            signature=make_signature(key_id="KEY-001"),
            key=make_key(key_id="KEY-999"),
        )


def test_service_rejects_signer_and_key_owner_mismatch() -> None:
    with pytest.raises(SignatureVerificationError, match="signer identity"):
        verify(
            signature=make_signature(
                signer_id="PROCESS-LINEAGE-CLASSIFIER"
            ),
            key=make_key(owner_id="OTHER-OWNER"),
        )


def test_service_rejects_algorithm_mismatch() -> None:
    key = make_key()
    object.__setattr__(key, "algorithm", "OTHER")
    with pytest.raises(SignatureVerificationError, match="algorithm"):
        verify(key=key)


def test_service_rejects_subject_identity_mismatch() -> None:
    with pytest.raises(SignatureVerificationError, match="subject identity"):
        verify(expected_subject_id="RIB-999")


def test_service_rejects_subject_type_mismatch() -> None:
    with pytest.raises(SignatureVerificationError, match="subject type"):
        verify(expected_subject_type="OTHER-TYPE")


def test_service_rejects_content_digest_mismatch() -> None:
    with pytest.raises(SignatureVerificationError, match="content digest"):
        verify(expected_content_digest="sha256:" + ("9" * 64))


def test_service_rejects_signature_before_key_validity() -> None:
    key = make_key(
        valid_from=datetime(2026, 7, 15, 12, 0, 1, tzinfo=timezone.utc)
    )
    with pytest.raises(
        SignatureVerificationError,
        match="before key validity",
    ):
        verify(key=key)


def test_service_rejects_signature_after_key_validity() -> None:
    key = make_key(
        valid_until=datetime(2026, 7, 15, 12, 0, 1, tzinfo=timezone.utc)
    )
    signature = make_signature(
        signed_at=datetime(2026, 7, 15, 12, 0, 2, tzinfo=timezone.utc)
    )
    with pytest.raises(
        SignatureVerificationError,
        match="after key validity",
    ):
        verify(
            signature=signature,
            key=key,
            verified_at=datetime(
                2026,
                7,
                15,
                12,
                0,
                3,
                tzinfo=timezone.utc,
            ),
        )


def test_service_rejects_revoked_key() -> None:
    with pytest.raises(SignatureVerificationError, match="revoked"):
        verify(key=make_key(revoked=True))


def test_service_rejects_naive_verified_at() -> None:
    with pytest.raises(SignatureVerificationError, match="timezone-aware"):
        verify(verified_at=datetime(2026, 7, 15, 12, 0))


def test_service_rejects_verification_before_signature() -> None:
    with pytest.raises(SignatureVerificationError, match="before signature"):
        verify(
            verified_at=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            )
        )


def test_service_does_not_mutate_inputs() -> None:
    signature = make_signature()
    key = make_key()
    original_signature = signature
    original_key = key
    verify(signature=signature, key=key)
    assert signature == original_signature
    assert key == original_key


def test_result_is_immutable() -> None:
    result = verify()
    with pytest.raises((AttributeError, TypeError)):
        result.verified = False  # type: ignore[misc]


def test_result_preserves_observer_only_boundary() -> None:
    result = verify()
    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_service_rejects_signature_after_key_validity() -> None:
    key = make_key(
        valid_until=datetime(
            2026,
            7,
            15,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        )
    )
    signature = make_signature(
        signed_at=datetime(
            2026,
            7,
            15,
            12,
            0,
            2,
            tzinfo=timezone.utc,
        )
    )

    with pytest.raises(
        SignatureVerificationError,
        match="after key validity",
    ):
        verify(
            signature=signature,
            key=key,
            verified_at=datetime(
                2026,
                7,
                15,
                12,
                0,
                3,
                tzinfo=timezone.utc,
            ),
        )