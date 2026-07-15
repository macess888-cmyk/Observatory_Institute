from datetime import datetime, timezone

import pytest

from models import DetachedSignature
from services.detached_signature_validator import (
    DetachedSignatureError,
    DetachedSignatureValidator,
)


SIGNED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
SIGNATURE_VALUE = "ed25519:" + ("a" * 128)


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


def test_validator_accepts_valid_detached_signature() -> None:
    signature = make_signature()

    assert DetachedSignatureValidator().validate(signature) is True


def test_signature_is_immutable() -> None:
    signature = make_signature()

    with pytest.raises((AttributeError, TypeError)):
        signature.signer_id = "OTHER"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "signature_id",
        "key_id",
        "subject_id",
        "subject_type",
        "algorithm",
        "signature_value",
        "signer_id",
    ],
)
def test_signature_rejects_empty_identity_or_value(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_signature(**{field_name: ""})


def test_signature_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        make_signature(algorithm="RSA")


@pytest.mark.parametrize(
    "digest",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
    ],
)
def test_signature_rejects_invalid_content_digest(
    digest: str,
) -> None:
    with pytest.raises(ValueError, match="content_digest"):
        make_signature(content_digest=digest)


def test_signature_rejects_invalid_signature_prefix() -> None:
    with pytest.raises(ValueError, match="signature_value"):
        make_signature(signature_value="rsa:invalid")


def test_signature_rejects_short_signature_value() -> None:
    with pytest.raises(ValueError, match="signature_value"):
        make_signature(signature_value="ed25519:abc")


def test_signature_rejects_non_hex_signature_value() -> None:
    with pytest.raises(ValueError, match="signature_value"):
        make_signature(
            signature_value="ed25519:" + ("z" * 128)
        )


def test_signature_rejects_naive_signed_at() -> None:
    with pytest.raises(
        ValueError,
        match="signed_at.*timezone-aware",
    ):
        make_signature(
            signed_at=datetime(2026, 7, 15, 12, 0),
        )


def test_validator_rejects_non_signature_input() -> None:
    with pytest.raises(TypeError, match="DetachedSignature"):
        DetachedSignatureValidator().validate(
            "SIG-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    signature = make_signature()

    assert (
        DetachedSignatureValidator().validate(
            signature,
            expected_key_id="KEY-001",
            expected_subject_id="RIB-001",
            expected_subject_type="RECOVERY_INTEGRITY_BUNDLE",
            expected_content_digest=CONTENT_DIGEST,
            expected_signer_id="PROCESS-LINEAGE-CLASSIFIER",
        )
        is True
    )


@pytest.mark.parametrize(
    (
        "expected_field",
        "expected_value",
        "error_match",
    ),
    [
        (
            "expected_key_id",
            "KEY-999",
            "key identity",
        ),
        (
            "expected_subject_id",
            "RIB-999",
            "subject identity",
        ),
        (
            "expected_subject_type",
            "OTHER-TYPE",
            "subject type",
        ),
        (
            "expected_content_digest",
            "sha256:" + ("9" * 64),
            "content digest",
        ),
        (
            "expected_signer_id",
            "OTHER-SIGNER",
            "signer identity",
        ),
    ],
)
def test_validator_rejects_reference_mismatch(
    expected_field: str,
    expected_value: str,
    error_match: str,
) -> None:
    arguments = {
        "expected_key_id": "KEY-001",
        "expected_subject_id": "RIB-001",
        "expected_subject_type": "RECOVERY_INTEGRITY_BUNDLE",
        "expected_content_digest": CONTENT_DIGEST,
        "expected_signer_id": "PROCESS-LINEAGE-CLASSIFIER",
    }
    arguments[expected_field] = expected_value

    with pytest.raises(
        DetachedSignatureError,
        match=error_match,
    ):
        DetachedSignatureValidator().validate(
            make_signature(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        DetachedSignatureError,
        match="complete expected reference set",
    ):
        DetachedSignatureValidator().validate(
            make_signature(),
            expected_key_id="KEY-001",
        )


def test_validator_does_not_mutate_signature() -> None:
    signature = make_signature()
    original = signature

    DetachedSignatureValidator().validate(signature)

    assert signature == original


def test_signature_preserves_observer_only_boundary() -> None:
    signature = make_signature()

    assert signature.execution_requested is False
    assert signature.side_effects_permitted is False