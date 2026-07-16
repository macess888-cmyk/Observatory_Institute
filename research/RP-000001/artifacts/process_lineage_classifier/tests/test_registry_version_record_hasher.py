import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import RegistryVersionRecord
from services.registry_version_record_hasher import (
    RegistryVersionRecordHashError,
    RegistryVersionRecordHasher,
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
        recorded_at=RECORDED_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    record = make_record()
    hasher = RegistryVersionRecordHasher()

    canonical = hasher.canonicalize(record)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(record) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = RegistryVersionRecordHasher().canonicalize(
        make_record()
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = RegistryVersionRecordHasher()
    record = make_record()

    assert hasher.hash(record) == hasher.hash(record)


def test_equivalent_records_produce_same_hash() -> None:
    hasher = RegistryVersionRecordHasher()

    assert hasher.hash(make_record()) == hasher.hash(
        make_record()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("record_id", "RVR-999"),
        ("registry_id", "TKR-999"),
        ("registry_version", "2.0.0"),
        ("previous_registry_version", "1.0.0"),
        ("snapshot_id", "TKRS-999"),
        ("previous_snapshot_id", "TKRS-001"),
        ("transition_type", "ADMISSION"),
        ("transition_receipt_id", "TKAR-999"),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = RegistryVersionRecordHasher()

    baseline = hasher.hash(make_record())
    changed = hasher.hash(
        make_record(**{field_name: value})
    )

    assert baseline != changed


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        RegistryVersionRecordHasher()
        .canonicalize(make_record())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = (
        RegistryVersionRecordHasher()
        .canonicalize(make_record())
    )

    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )

    assert tuple(decoded.keys()) == (
        "record_id",
        "registry_id",
        "registry_version",
        "previous_registry_version",
        "snapshot_id",
        "snapshot_digest",
        "previous_snapshot_id",
        "previous_snapshot_digest",
        "transition_type",
        "transition_receipt_id",
        "transition_receipt_digest",
        "recorded_at",
        "owner_id",
        "issuer_id",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamp() -> None:
    canonical_text = (
        RegistryVersionRecordHasher()
        .canonicalize(make_record())
        .decode("utf-8")
    )

    assert RECORDED_AT.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = RegistryVersionRecordHasher().canonicalize(
        make_record()
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["record_id"] == "RVR-001"
    assert decoded["transition_type"] == "REMOVAL"
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_record_input() -> None:
    with pytest.raises(
        TypeError,
        match="RegistryVersionRecord",
    ):
        RegistryVersionRecordHasher().hash(
            "RVR-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_record_input() -> None:
    with pytest.raises(
        TypeError,
        match="RegistryVersionRecord",
    ):
        RegistryVersionRecordHasher().canonicalize(
            "RVR-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = RegistryVersionRecordHasher()
    record = make_record()
    digest = hasher.hash(record)

    assert hasher.validate(record, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        RegistryVersionRecordHashError,
        match="hash mismatch",
    ):
        RegistryVersionRecordHasher().validate(
            make_record(),
            "sha256:" + ("9" * 64),
        )


@pytest.mark.parametrize(
    "digest",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
        "sha256:" + ("A" * 64),
    ],
)
def test_validate_rejects_invalid_expected_digest(
    digest: str,
) -> None:
    with pytest.raises(
        RegistryVersionRecordHashError,
        match="expected_digest",
    ):
        RegistryVersionRecordHasher().validate(
            make_record(),
            digest,
        )


def test_hasher_does_not_mutate_record() -> None:
    record = make_record()
    original = record

    RegistryVersionRecordHasher().hash(record)

    assert record == original


def test_record_preserves_observer_only_boundary() -> None:
    record = make_record()

    assert record.execution_requested is False
    assert record.side_effects_permitted is False