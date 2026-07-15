from datetime import datetime, timezone

import pytest

from models import KeyRevocationRecord
from services.key_revocation_record_validator import (
    KeyRevocationRecordError,
    KeyRevocationRecordValidator,
)


REVOKED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
KEY_FINGERPRINT = "sha256:" + ("1" * 64)


def make_revocation(
    *,
    revocation_id: str = "KRV-001",
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    key_fingerprint: str = KEY_FINGERPRINT,
    algorithm: str = "ED25519",
    revoked_at: datetime = REVOKED_AT,
    revoked_by: str = "OBSERVATORY-INSTITUTE",
    reason: str = "Key compromised.",
    permanent: bool = True,
) -> KeyRevocationRecord:
    return KeyRevocationRecord(
        revocation_id=revocation_id,
        key_id=key_id,
        owner_id=owner_id,
        key_fingerprint=key_fingerprint,
        algorithm=algorithm,
        revoked_at=revoked_at,
        revoked_by=revoked_by,
        reason=reason,
        permanent=permanent,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_revocation_record() -> None:
    record = make_revocation()

    assert KeyRevocationRecordValidator().validate(record) is True


def test_revocation_record_is_immutable() -> None:
    record = make_revocation()

    with pytest.raises((AttributeError, TypeError)):
        record.permanent = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "revocation_id",
        "key_id",
        "owner_id",
        "algorithm",
        "revoked_by",
        "reason",
    ],
)
def test_revocation_record_rejects_empty_value(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_revocation(**{field_name: ""})


def test_revocation_record_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        make_revocation(algorithm="RSA")


@pytest.mark.parametrize(
    "fingerprint",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
    ],
)
def test_revocation_record_rejects_invalid_fingerprint(
    fingerprint: str,
) -> None:
    with pytest.raises(ValueError, match="key_fingerprint"):
        make_revocation(key_fingerprint=fingerprint)


def test_revocation_record_rejects_naive_revoked_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_revocation(
            revoked_at=datetime(2026, 7, 15, 12, 0)
        )


def test_revocation_record_rejects_non_boolean_permanent() -> None:
    with pytest.raises(TypeError, match="permanent"):
        make_revocation(
            permanent="true",  # type: ignore[arg-type]
        )


def test_validator_rejects_non_revocation_record_input() -> None:
    with pytest.raises(TypeError, match="KeyRevocationRecord"):
        KeyRevocationRecordValidator().validate(
            "KRV-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    record = make_revocation()

    assert (
        KeyRevocationRecordValidator().validate(
            record,
            expected_key_id="KEY-001",
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_fingerprint=KEY_FINGERPRINT,
            expected_algorithm="ED25519",
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
            "expected_owner_id",
            "OTHER-OWNER",
            "owner identity",
        ),
        (
            "expected_fingerprint",
            "sha256:" + ("9" * 64),
            "key fingerprint",
        ),
        (
            "expected_algorithm",
            "OTHER",
            "algorithm",
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
        "expected_owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "expected_fingerprint": KEY_FINGERPRINT,
        "expected_algorithm": "ED25519",
    }
    arguments[expected_field] = expected_value

    with pytest.raises(
        KeyRevocationRecordError,
        match=error_match,
    ):
        KeyRevocationRecordValidator().validate(
            make_revocation(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        KeyRevocationRecordError,
        match="complete expected reference set",
    ):
        KeyRevocationRecordValidator().validate(
            make_revocation(),
            expected_key_id="KEY-001",
        )


def test_validator_rejects_non_permanent_revocation() -> None:
    with pytest.raises(
        KeyRevocationRecordError,
        match="permanent",
    ):
        KeyRevocationRecordValidator().validate(
            make_revocation(permanent=False)
        )


def test_validator_does_not_mutate_record() -> None:
    record = make_revocation()
    original = record

    KeyRevocationRecordValidator().validate(record)

    assert record == original


def test_revocation_record_preserves_observer_only_boundary() -> None:
    record = make_revocation()

    assert record.execution_requested is False
    assert record.side_effects_permitted is False