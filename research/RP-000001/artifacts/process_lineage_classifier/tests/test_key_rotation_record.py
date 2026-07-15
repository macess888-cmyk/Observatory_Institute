from datetime import datetime, timezone

import pytest

from models import KeyRotationRecord
from services.key_rotation_record_validator import (
    KeyRotationRecordError,
    KeyRotationRecordValidator,
)


ROTATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

PREVIOUS_FINGERPRINT = "sha256:" + ("1" * 64)
NEW_FINGERPRINT = "sha256:" + ("2" * 64)


def make_rotation(
    *,
    rotation_id: str = "KRR-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    previous_key_id: str = "KEY-001",
    previous_key_fingerprint: str = PREVIOUS_FINGERPRINT,
    new_key_id: str = "KEY-002",
    new_key_fingerprint: str = NEW_FINGERPRINT,
    algorithm: str = "ED25519",
    rotated_at: datetime = ROTATED_AT,
    rotated_by: str = "OBSERVATORY-INSTITUTE",
    reason: str = "Scheduled key rotation.",
) -> KeyRotationRecord:
    return KeyRotationRecord(
        rotation_id=rotation_id,
        owner_id=owner_id,
        previous_key_id=previous_key_id,
        previous_key_fingerprint=previous_key_fingerprint,
        new_key_id=new_key_id,
        new_key_fingerprint=new_key_fingerprint,
        algorithm=algorithm,
        rotated_at=rotated_at,
        rotated_by=rotated_by,
        reason=reason,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_rotation_record() -> None:
    record = make_rotation()

    assert KeyRotationRecordValidator().validate(record) is True


def test_rotation_record_is_immutable() -> None:
    record = make_rotation()

    with pytest.raises((AttributeError, TypeError)):
        record.new_key_id = "KEY-999"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "rotation_id",
        "owner_id",
        "previous_key_id",
        "new_key_id",
        "algorithm",
        "rotated_by",
        "reason",
    ],
)
def test_rotation_record_rejects_empty_value(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_rotation(**{field_name: ""})


def test_rotation_record_rejects_same_key_identity() -> None:
    with pytest.raises(ValueError, match="different"):
        make_rotation(new_key_id="KEY-001")


def test_rotation_record_rejects_same_key_fingerprint() -> None:
    with pytest.raises(ValueError, match="different"):
        make_rotation(
            new_key_fingerprint=PREVIOUS_FINGERPRINT,
        )


def test_rotation_record_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        make_rotation(algorithm="RSA")


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("previous_key_fingerprint", "md5:invalid"),
        ("new_key_fingerprint", "md5:invalid"),
        ("previous_key_fingerprint", "sha256:abc"),
        ("new_key_fingerprint", "sha256:abc"),
        (
            "previous_key_fingerprint",
            "sha256:" + ("z" * 64),
        ),
        (
            "new_key_fingerprint",
            "sha256:" + ("z" * 64),
        ),
    ],
)
def test_rotation_record_rejects_invalid_fingerprint(
    field_name: str,
    value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_rotation(**{field_name: value})


def test_rotation_record_rejects_naive_rotated_at() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        make_rotation(
            rotated_at=datetime(2026, 7, 15, 12, 0),
        )


def test_validator_rejects_non_rotation_record_input() -> None:
    with pytest.raises(TypeError, match="KeyRotationRecord"):
        KeyRotationRecordValidator().validate(
            "KRR-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    record = make_rotation()

    assert (
        KeyRotationRecordValidator().validate(
            record,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_previous_key_id="KEY-001",
            expected_previous_fingerprint=PREVIOUS_FINGERPRINT,
            expected_new_key_id="KEY-002",
            expected_new_fingerprint=NEW_FINGERPRINT,
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
            "expected_owner_id",
            "OTHER-OWNER",
            "owner identity",
        ),
        (
            "expected_previous_key_id",
            "KEY-999",
            "previous key identity",
        ),
        (
            "expected_previous_fingerprint",
            "sha256:" + ("8" * 64),
            "previous key fingerprint",
        ),
        (
            "expected_new_key_id",
            "KEY-999",
            "new key identity",
        ),
        (
            "expected_new_fingerprint",
            "sha256:" + ("9" * 64),
            "new key fingerprint",
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
        "expected_owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "expected_previous_key_id": "KEY-001",
        "expected_previous_fingerprint": PREVIOUS_FINGERPRINT,
        "expected_new_key_id": "KEY-002",
        "expected_new_fingerprint": NEW_FINGERPRINT,
        "expected_algorithm": "ED25519",
    }
    arguments[expected_field] = expected_value

    with pytest.raises(
        KeyRotationRecordError,
        match=error_match,
    ):
        KeyRotationRecordValidator().validate(
            make_rotation(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        KeyRotationRecordError,
        match="complete expected reference set",
    ):
        KeyRotationRecordValidator().validate(
            make_rotation(),
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_validator_does_not_mutate_record() -> None:
    record = make_rotation()
    original = record

    KeyRotationRecordValidator().validate(record)

    assert record == original


def test_rotation_record_preserves_observer_only_boundary() -> None:
    record = make_rotation()

    assert record.execution_requested is False
    assert record.side_effects_permitted is False