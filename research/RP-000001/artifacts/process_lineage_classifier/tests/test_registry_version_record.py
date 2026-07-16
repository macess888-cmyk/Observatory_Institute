from datetime import datetime, timezone

import pytest

from models import RegistryVersionRecord
from services.registry_version_record_validator import (
    RegistryVersionRecordError,
    RegistryVersionRecordValidator,
)


RECORDED_AT = datetime(2026, 7, 15, 14, 30, tzinfo=timezone.utc)

SNAPSHOT_DIGEST = "sha256:" + ("1" * 64)
PREVIOUS_SNAPSHOT_DIGEST = "sha256:" + ("2" * 64)
TRANSITION_RECEIPT_DIGEST = "sha256:" + ("3" * 64)


def make_record(
    *,
    record_id: str = "RVR-001",
    registry_id: str = "TKR-001",
    registry_version: str = "1.2.0",
    previous_registry_version: str = "1.1.0",
    snapshot_id: str = "TKRS-003",
    previous_snapshot_id: str = "TKRS-002",
    transition_type: str = "REMOVAL",
    transition_receipt_id: str = "TKRR-001",
    recorded_at: datetime = RECORDED_AT,
) -> RegistryVersionRecord:
    return RegistryVersionRecord(
        record_id=record_id,
        registry_id=registry_id,
        registry_version=registry_version,
        previous_registry_version=previous_registry_version,
        snapshot_id=snapshot_id,
        snapshot_digest=SNAPSHOT_DIGEST,
        previous_snapshot_id=previous_snapshot_id,
        previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
        transition_type=transition_type,
        transition_receipt_id=transition_receipt_id,
        transition_receipt_digest=TRANSITION_RECEIPT_DIGEST,
        recorded_at=recorded_at,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_record() -> None:
    record = make_record()

    assert RegistryVersionRecordValidator().validate(
        record
    ) is True


def test_record_is_immutable() -> None:
    record = make_record()

    with pytest.raises((AttributeError, TypeError)):
        record.registry_version = "2.0.0"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "record_id",
        "registry_id",
        "registry_version",
        "previous_registry_version",
        "snapshot_id",
        "previous_snapshot_id",
        "transition_type",
        "transition_receipt_id",
    ],
)
def test_record_rejects_empty_identity(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_record(**{field_name: ""})


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("snapshot_digest", "md5:invalid"),
        ("previous_snapshot_digest", "sha256:abc"),
        (
            "transition_receipt_digest",
            "sha256:" + ("z" * 64),
        ),
    ],
)
def test_record_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "record_id": "RVR-001",
        "registry_id": "TKR-001",
        "registry_version": "1.2.0",
        "previous_registry_version": "1.1.0",
        "snapshot_id": "TKRS-003",
        "snapshot_digest": SNAPSHOT_DIGEST,
        "previous_snapshot_id": "TKRS-002",
        "previous_snapshot_digest": PREVIOUS_SNAPSHOT_DIGEST,
        "transition_type": "REMOVAL",
        "transition_receipt_id": "TKRR-001",
        "transition_receipt_digest": TRANSITION_RECEIPT_DIGEST,
        "recorded_at": RECORDED_AT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    arguments[field_name] = value

    with pytest.raises(ValueError, match=field_name):
        RegistryVersionRecord(**arguments)


def test_record_rejects_same_registry_version() -> None:
    with pytest.raises(
        ValueError,
        match="registry version transition",
    ):
        make_record(
            registry_version="1.1.0",
            previous_registry_version="1.1.0",
        )


def test_record_rejects_same_snapshot_identity() -> None:
    with pytest.raises(
        ValueError,
        match="snapshot transition",
    ):
        make_record(
            snapshot_id="TKRS-002",
            previous_snapshot_id="TKRS-002",
        )


def test_record_rejects_same_snapshot_digest() -> None:
    with pytest.raises(
        ValueError,
        match="snapshot digest transition",
    ):
        RegistryVersionRecord(
            record_id="RVR-001",
            registry_id="TKR-001",
            registry_version="1.2.0",
            previous_registry_version="1.1.0",
            snapshot_id="TKRS-003",
            snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            previous_snapshot_id="TKRS-002",
            previous_snapshot_digest=PREVIOUS_SNAPSHOT_DIGEST,
            transition_type="REMOVAL",
            transition_receipt_id="TKRR-001",
            transition_receipt_digest=TRANSITION_RECEIPT_DIGEST,
            recorded_at=RECORDED_AT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            execution_requested=False,
            side_effects_permitted=False,
        )


@pytest.mark.parametrize(
    "transition_type",
    [
        "ADMISSION",
        "REMOVAL",
    ],
)
def test_record_accepts_supported_transition_type(
    transition_type: str,
) -> None:
    record = make_record(
        transition_type=transition_type
    )

    assert record.transition_type == transition_type


def test_record_rejects_unsupported_transition_type() -> None:
    with pytest.raises(
        ValueError,
        match="transition_type",
    ):
        make_record(transition_type="OTHER")


def test_record_rejects_naive_recorded_at() -> None:
    with pytest.raises(
        ValueError,
        match="recorded_at.*timezone-aware",
    ):
        make_record(
            recorded_at=datetime(2026, 7, 15, 14, 30)
        )


def test_validator_rejects_non_record_input() -> None:
    with pytest.raises(
        TypeError,
        match="RegistryVersionRecord",
    ):
        RegistryVersionRecordValidator().validate(
            "RVR-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    record = make_record()

    assert RegistryVersionRecordValidator().validate(
        record,
        expected_registry_id="TKR-001",
        expected_registry_version="1.2.0",
        expected_previous_registry_version="1.1.0",
        expected_snapshot_id="TKRS-003",
        expected_previous_snapshot_id="TKRS-002",
        expected_transition_type="REMOVAL",
        expected_transition_receipt_id="TKRR-001",
    ) is True


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
        "error_match",
    ),
    [
        (
            "expected_registry_id",
            "TKR-999",
            "registry identity",
        ),
        (
            "expected_registry_version",
            "9.9.9",
            "registry version",
        ),
        (
            "expected_previous_registry_version",
            "0.0.0",
            "previous registry version",
        ),
        (
            "expected_snapshot_id",
            "TKRS-999",
            "snapshot identity",
        ),
        (
            "expected_previous_snapshot_id",
            "TKRS-000",
            "previous snapshot identity",
        ),
        (
            "expected_transition_type",
            "ADMISSION",
            "transition type",
        ),
        (
            "expected_transition_receipt_id",
            "TKAR-999",
            "transition receipt identity",
        ),
    ],
)
def test_validator_rejects_reference_mismatch(
    field_name: str,
    value: str,
    error_match: str,
) -> None:
    arguments = {
        "expected_registry_id": "TKR-001",
        "expected_registry_version": "1.2.0",
        "expected_previous_registry_version": "1.1.0",
        "expected_snapshot_id": "TKRS-003",
        "expected_previous_snapshot_id": "TKRS-002",
        "expected_transition_type": "REMOVAL",
        "expected_transition_receipt_id": "TKRR-001",
    }
    arguments[field_name] = value

    with pytest.raises(
        RegistryVersionRecordError,
        match=error_match,
    ):
        RegistryVersionRecordValidator().validate(
            make_record(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        RegistryVersionRecordError,
        match="complete expected reference set",
    ):
        RegistryVersionRecordValidator().validate(
            make_record(),
            expected_registry_id="TKR-001",
        )


def test_validator_does_not_mutate_record() -> None:
    record = make_record()
    original = record

    RegistryVersionRecordValidator().validate(record)

    assert record == original


def test_record_preserves_observer_only_boundary() -> None:
    record = make_record()

    assert record.execution_requested is False
    assert record.side_effects_permitted is False