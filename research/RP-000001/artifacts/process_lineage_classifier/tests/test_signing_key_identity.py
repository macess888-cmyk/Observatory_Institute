from datetime import datetime, timezone

import pytest

from models import SigningKeyIdentity
from services.signing_key_identity_validator import (
    SigningKeyIdentityError,
    SigningKeyIdentityValidator,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_FROM = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)
REFERENCE_TIME = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

VALID_FINGERPRINT = (
    "sha256:"
    + ("1" * 64)
)


def make_key(
    *,
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    algorithm: str = "ED25519",
    public_key_fingerprint: str = VALID_FINGERPRINT,
    created_at: datetime = CREATED_AT,
    valid_from: datetime = VALID_FROM,
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


def test_validator_accepts_valid_signing_key() -> None:
    key = make_key()

    assert (
        SigningKeyIdentityValidator().validate(
            key,
            now=REFERENCE_TIME,
        )
        is True
    )


def test_key_is_immutable() -> None:
    key = make_key()

    with pytest.raises((AttributeError, TypeError)):
        key.revoked = True  # type: ignore[misc]


def test_key_rejects_empty_key_id() -> None:
    with pytest.raises(ValueError, match="key_id"):
        make_key(key_id="")


def test_key_rejects_empty_owner_id() -> None:
    with pytest.raises(ValueError, match="owner_id"):
        make_key(owner_id="")


def test_key_rejects_empty_issuer_id() -> None:
    with pytest.raises(ValueError, match="issuer_id"):
        make_key(issuer_id="")


def test_key_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        make_key(algorithm="RSA")


def test_key_rejects_empty_algorithm() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        make_key(algorithm="")


@pytest.mark.parametrize(
    "fingerprint",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
    ],
)
def test_key_rejects_invalid_fingerprint(
    fingerprint: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="public_key_fingerprint",
    ):
        make_key(
            public_key_fingerprint=fingerprint,
        )


def test_key_rejects_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="created_at.*timezone-aware",
    ):
        make_key(
            created_at=datetime(2026, 7, 15, 12, 0),
        )


def test_key_rejects_naive_valid_from() -> None:
    with pytest.raises(
        ValueError,
        match="valid_from.*timezone-aware",
    ):
        make_key(
            valid_from=datetime(2026, 7, 15, 12, 0),
        )


def test_key_rejects_naive_valid_until() -> None:
    with pytest.raises(
        ValueError,
        match="valid_until.*timezone-aware",
    ):
        make_key(
            valid_until=datetime(2027, 7, 15, 12, 0),
        )


def test_key_rejects_valid_from_before_creation() -> None:
    with pytest.raises(
        ValueError,
        match="valid_from",
    ):
        make_key(
            valid_from=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            )
        )


def test_key_rejects_valid_until_before_valid_from() -> None:
    with pytest.raises(
        ValueError,
        match="valid_until",
    ):
        make_key(
            valid_until=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            )
        )


def test_key_rejects_equal_validity_boundaries() -> None:
    with pytest.raises(
        ValueError,
        match="valid_until",
    ):
        make_key(
            valid_until=VALID_FROM,
        )


def test_key_rejects_non_boolean_revoked() -> None:
    with pytest.raises(TypeError, match="revoked"):
        make_key(
            revoked="false",  # type: ignore[arg-type]
        )


def test_validator_rejects_non_key_input() -> None:
    with pytest.raises(
        TypeError,
        match="SigningKeyIdentity",
    ):
        SigningKeyIdentityValidator().validate(
            "KEY-001",  # type: ignore[arg-type]
            now=REFERENCE_TIME,
        )


def test_validator_rejects_naive_reference_time() -> None:
    with pytest.raises(
        SigningKeyIdentityError,
        match="timezone-aware",
    ):
        SigningKeyIdentityValidator().validate(
            make_key(),
            now=datetime(2026, 8, 1, 12, 0),
        )


def test_validator_rejects_time_before_validity_window() -> None:
    with pytest.raises(
        SigningKeyIdentityError,
        match="not yet valid",
    ):
        SigningKeyIdentityValidator().validate(
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


def test_validator_rejects_time_after_validity_window() -> None:
    with pytest.raises(
        SigningKeyIdentityError,
        match="expired",
    ):
        SigningKeyIdentityValidator().validate(
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


def test_validator_accepts_valid_from_boundary() -> None:
    assert (
        SigningKeyIdentityValidator().validate(
            make_key(),
            now=VALID_FROM,
        )
        is True
    )


def test_validator_accepts_valid_until_boundary() -> None:
    assert (
        SigningKeyIdentityValidator().validate(
            make_key(),
            now=VALID_UNTIL,
        )
        is True
    )


def test_validator_rejects_revoked_key() -> None:
    with pytest.raises(
        SigningKeyIdentityError,
        match="revoked",
    ):
        SigningKeyIdentityValidator().validate(
            make_key(revoked=True),
            now=REFERENCE_TIME,
        )


def test_validator_accepts_expected_owner_and_issuer() -> None:
    key = make_key()

    assert (
        SigningKeyIdentityValidator().validate(
            key,
            now=REFERENCE_TIME,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_issuer_id="OBSERVATORY-INSTITUTE",
        )
        is True
    )


def test_validator_rejects_owner_mismatch() -> None:
    with pytest.raises(
        SigningKeyIdentityError,
        match="owner identity",
    ):
        SigningKeyIdentityValidator().validate(
            make_key(),
            now=REFERENCE_TIME,
            expected_owner_id="OTHER-OWNER",
            expected_issuer_id="OBSERVATORY-INSTITUTE",
        )


def test_validator_rejects_issuer_mismatch() -> None:
    with pytest.raises(
        SigningKeyIdentityError,
        match="issuer identity",
    ):
        SigningKeyIdentityValidator().validate(
            make_key(),
            now=REFERENCE_TIME,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_issuer_id="OTHER-ISSUER",
        )


def test_validator_does_not_mutate_key() -> None:
    key = make_key()
    original = key

    SigningKeyIdentityValidator().validate(
        key,
        now=REFERENCE_TIME,
    )

    assert key == original


def test_key_preserves_observer_only_boundary() -> None:
    key = make_key()

    assert key.execution_requested is False
    assert key.side_effects_permitted is False