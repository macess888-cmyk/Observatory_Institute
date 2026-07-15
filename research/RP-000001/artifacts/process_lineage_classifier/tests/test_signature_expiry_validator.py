from datetime import datetime, timezone

import pytest

from models import DetachedSignature, SigningKeyIdentity
from services.signature_expiry_validator import (
    SignatureExpiryError,
    SignatureExpiryValidator,
)


SIGNED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_FROM = datetime(2026, 7, 15, 11, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)
REFERENCE_TIME = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
KEY_FINGERPRINT = "sha256:" + ("2" * 64)
SIGNATURE_VALUE = "ed25519:" + ("a" * 128)


def make_key(
    *,
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    created_at: datetime = VALID_FROM,
    valid_from: datetime = VALID_FROM,
    valid_until: datetime = VALID_UNTIL,
    revoked: bool = False,
) -> SigningKeyIdentity:
    return SigningKeyIdentity(
        key_id=key_id,
        owner_id=owner_id,
        algorithm="ED25519",
        public_key_fingerprint=KEY_FINGERPRINT,
        created_at=created_at,
        valid_from=valid_from,
        valid_until=valid_until,
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=revoked,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_signature(
    *,
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    signed_at: datetime = SIGNED_AT,
    signer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> DetachedSignature:
    return DetachedSignature(
        signature_id=signature_id,
        key_id=key_id,
        subject_id="RIB-001",
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=CONTENT_DIGEST,
        algorithm="ED25519",
        signature_value=SIGNATURE_VALUE,
        signed_at=signed_at,
        signer_id=signer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_unexpired_signature() -> None:
    assert SignatureExpiryValidator().validate(
        make_signature(),
        make_key(),
        now=REFERENCE_TIME,
    ) is True


def test_validator_rejects_non_signature_input() -> None:
    with pytest.raises(TypeError, match="DetachedSignature"):
        SignatureExpiryValidator().validate(
            "SIG-001",  # type: ignore[arg-type]
            make_key(),
            now=REFERENCE_TIME,
        )


def test_validator_rejects_non_key_input() -> None:
    with pytest.raises(TypeError, match="SigningKeyIdentity"):
        SignatureExpiryValidator().validate(
            make_signature(),
            "KEY-001",  # type: ignore[arg-type]
            now=REFERENCE_TIME,
        )


def test_validator_rejects_naive_reference_time() -> None:
    with pytest.raises(
        SignatureExpiryError,
        match="timezone-aware",
    ):
        SignatureExpiryValidator().validate(
            make_signature(),
            make_key(),
            now=datetime(2026, 8, 1, 12, 0),
        )


def test_validator_rejects_key_identity_mismatch() -> None:
    with pytest.raises(
        SignatureExpiryError,
        match="key identity",
    ):
        SignatureExpiryValidator().validate(
            make_signature(key_id="KEY-001"),
            make_key(key_id="KEY-999"),
            now=REFERENCE_TIME,
        )


def test_validator_rejects_signer_owner_mismatch() -> None:
    with pytest.raises(
        SignatureExpiryError,
        match="signer identity",
    ):
        SignatureExpiryValidator().validate(
            make_signature(),
            make_key(owner_id="OTHER-OWNER"),
            now=REFERENCE_TIME,
        )


def test_validator_rejects_signature_before_key_validity() -> None:
    signature = make_signature(
        signed_at=datetime(
            2026,
            7,
            15,
            10,
            59,
            59,
            tzinfo=timezone.utc,
        )
    )

    with pytest.raises(
        SignatureExpiryError,
        match="before key validity",
    ):
        SignatureExpiryValidator().validate(
            signature,
            make_key(),
            now=REFERENCE_TIME,
        )


def test_validator_rejects_signature_after_key_validity() -> None:
    signature = make_signature(
        signed_at=datetime(
            2027,
            7,
            15,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        )
    )

    with pytest.raises(
        SignatureExpiryError,
        match="after key validity",
    ):
        SignatureExpiryValidator().validate(
            signature,
            make_key(),
            now=datetime(
                2027,
                7,
                15,
                12,
                0,
                2,
                tzinfo=timezone.utc,
            ),
        )


def test_validator_rejects_revoked_key() -> None:
    with pytest.raises(
        SignatureExpiryError,
        match="revoked",
    ):
        SignatureExpiryValidator().validate(
            make_signature(),
            make_key(revoked=True),
            now=REFERENCE_TIME,
        )


def test_validator_rejects_current_time_before_signature() -> None:
    with pytest.raises(
        SignatureExpiryError,
        match="before signature",
    ):
        SignatureExpiryValidator().validate(
            make_signature(),
            make_key(),
            now=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            ),
        )


def test_validator_rejects_expired_key_at_reference_time() -> None:
    with pytest.raises(
        SignatureExpiryError,
        match="expired",
    ):
        SignatureExpiryValidator().validate(
            make_signature(),
            make_key(),
            now=datetime(
                2027,
                7,
                15,
                12,
                0,
                1,
                tzinfo=timezone.utc,
            ),
        )


def test_validator_accepts_valid_until_boundary() -> None:
    assert SignatureExpiryValidator().validate(
        make_signature(),
        make_key(),
        now=VALID_UNTIL,
    ) is True


def test_validator_accepts_signature_at_valid_from_boundary() -> None:
    assert SignatureExpiryValidator().validate(
        make_signature(signed_at=VALID_FROM),
        make_key(),
        now=REFERENCE_TIME,
    ) is True


def test_validator_accepts_signature_at_valid_until_boundary() -> None:
    assert SignatureExpiryValidator().validate(
        make_signature(signed_at=VALID_UNTIL),
        make_key(),
        now=VALID_UNTIL,
    ) is True


def test_validator_does_not_mutate_inputs() -> None:
    signature = make_signature()
    key = make_key()
    original_signature = signature
    original_key = key

    SignatureExpiryValidator().validate(
        signature,
        key,
        now=REFERENCE_TIME,
    )

    assert signature == original_signature
    assert key == original_key


def test_signature_and_key_preserve_observer_only_boundary() -> None:
    signature = make_signature()
    key = make_key()

    assert signature.execution_requested is False
    assert signature.side_effects_permitted is False
    assert key.execution_requested is False
    assert key.side_effects_permitted is False