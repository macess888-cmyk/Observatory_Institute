import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import (
    PublicKeyMaterial,
    TrustedKeyRegistrySnapshot,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)
from services.trusted_key_registry_snapshot_hasher import (
    TrustedKeyRegistrySnapshotHashError,
    TrustedKeyRegistrySnapshotHasher,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
CAPTURED_AT = datetime(2026, 7, 15, 12, 30, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)

PUBLIC_KEY_VALUE_001 = "ed25519:" + ("a" * 64)
PUBLIC_KEY_VALUE_002 = "ed25519:" + ("b" * 64)

FINGERPRINT_001 = PublicKeyFingerprintService().generate(
    PUBLIC_KEY_VALUE_001
)
FINGERPRINT_002 = PublicKeyFingerprintService().generate(
    PUBLIC_KEY_VALUE_002
)


def make_material(
    *,
    material_id: str,
    key_id: str,
    public_key_value: str,
    public_key_fingerprint: str,
) -> PublicKeyMaterial:
    return PublicKeyMaterial(
        material_id=material_id,
        key_id=key_id,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        algorithm="ED25519",
        encoding="HEX",
        public_key_value=public_key_value,
        public_key_fingerprint=public_key_fingerprint,
        created_at=CREATED_AT,
        valid_from=CREATED_AT,
        valid_until=VALID_UNTIL,
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_snapshot(
    *,
    snapshot_id: str = "TKRS-001",
    registry_id: str = "TKR-001",
    registry_version: str = "1.0.0",
    materials: tuple[PublicKeyMaterial, ...] | None = None,
    captured_at: datetime = CAPTURED_AT,
) -> TrustedKeyRegistrySnapshot:
    if materials is None:
        materials = (
            make_material(
                material_id="PKM-001",
                key_id="KEY-001",
                public_key_value=PUBLIC_KEY_VALUE_001,
                public_key_fingerprint=FINGERPRINT_001,
            ),
            make_material(
                material_id="PKM-002",
                key_id="KEY-002",
                public_key_value=PUBLIC_KEY_VALUE_002,
                public_key_fingerprint=FINGERPRINT_002,
            ),
        )

    return TrustedKeyRegistrySnapshot(
        snapshot_id=snapshot_id,
        registry_id=registry_id,
        registry_version=registry_version,
        materials=materials,
        captured_at=captured_at,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    snapshot = make_snapshot()
    hasher = TrustedKeyRegistrySnapshotHasher()

    canonical = hasher.canonicalize(snapshot)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(snapshot) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = TrustedKeyRegistrySnapshotHasher().canonicalize(
        make_snapshot()
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = TrustedKeyRegistrySnapshotHasher()
    snapshot = make_snapshot()

    assert hasher.hash(snapshot) == hasher.hash(snapshot)


def test_equivalent_snapshots_produce_same_hash() -> None:
    hasher = TrustedKeyRegistrySnapshotHasher()

    assert hasher.hash(make_snapshot()) == hasher.hash(
        make_snapshot()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("snapshot_id", "TKRS-999"),
        ("registry_id", "TKR-999"),
        ("registry_version", "9.9.9"),
        (
            "captured_at",
            datetime(
                2026,
                7,
                15,
                12,
                31,
                tzinfo=timezone.utc,
            ),
        ),
    ],
)
def test_changed_snapshot_field_changes_hash(
    field_name: str,
    value: object,
) -> None:
    hasher = TrustedKeyRegistrySnapshotHasher()

    baseline = hasher.hash(make_snapshot())
    changed = hasher.hash(
        make_snapshot(**{field_name: value})
    )

    assert baseline != changed


def test_changed_material_changes_hash() -> None:
    hasher = TrustedKeyRegistrySnapshotHasher()
    first = make_snapshot()

    changed_material = make_material(
        material_id="PKM-003",
        key_id="KEY-003",
        public_key_value="ed25519:" + ("c" * 64),
        public_key_fingerprint=(
            PublicKeyFingerprintService().generate(
                "ed25519:" + ("c" * 64)
            )
        ),
    )

    second = make_snapshot(
        materials=(
            first.materials[0],
            changed_material,
        )
    )

    assert hasher.hash(first) != hasher.hash(second)


def test_material_order_changes_hash() -> None:
    hasher = TrustedKeyRegistrySnapshotHasher()
    snapshot = make_snapshot()

    reversed_snapshot = make_snapshot(
        materials=tuple(reversed(snapshot.materials))
    )

    assert hasher.hash(snapshot) != hasher.hash(
        reversed_snapshot
    )


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        TrustedKeyRegistrySnapshotHasher()
        .canonicalize(make_snapshot())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_top_level_order() -> None:
    canonical = (
        TrustedKeyRegistrySnapshotHasher()
        .canonicalize(make_snapshot())
    )

    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )

    assert tuple(decoded.keys()) == (
        "snapshot_id",
        "registry_id",
        "registry_version",
        "materials",
        "captured_at",
        "owner_id",
        "issuer_id",
        "execution_requested",
        "side_effects_permitted",
    )


def test_material_payload_uses_expected_field_order() -> None:
    canonical_text = (
        TrustedKeyRegistrySnapshotHasher()
        .canonicalize(make_snapshot())
        .decode("utf-8")
    )

    first_material_start = canonical_text.index(
        '"material_id"'
    )
    first_material_end = canonical_text.index(
        "}",
        first_material_start,
    )
    first_material = canonical_text[
        first_material_start:first_material_end
    ]

    expected_order = (
        '"material_id"',
        '"key_id"',
        '"owner_id"',
        '"algorithm"',
        '"encoding"',
        '"public_key_value"',
        '"public_key_fingerprint"',
        '"created_at"',
        '"valid_from"',
        '"valid_until"',
        '"issuer_id"',
        '"revoked"',
        '"execution_requested"',
        '"side_effects_permitted"',
    )

    positions = tuple(
        first_material.index(field_name)
        for field_name in expected_order
    )

    assert positions == tuple(sorted(positions))


def test_canonical_payload_uses_iso_timestamps() -> None:
    canonical_text = (
        TrustedKeyRegistrySnapshotHasher()
        .canonicalize(make_snapshot())
        .decode("utf-8")
    )

    assert CAPTURED_AT.isoformat() in canonical_text
    assert CREATED_AT.isoformat() in canonical_text
    assert VALID_UNTIL.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = TrustedKeyRegistrySnapshotHasher().canonicalize(
        make_snapshot()
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["snapshot_id"] == "TKRS-001"
    assert len(decoded["materials"]) == 2


def test_hasher_rejects_non_snapshot_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyRegistrySnapshot",
    ):
        TrustedKeyRegistrySnapshotHasher().hash(
            "TKRS-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_snapshot_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyRegistrySnapshot",
    ):
        TrustedKeyRegistrySnapshotHasher().canonicalize(
            "TKRS-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = TrustedKeyRegistrySnapshotHasher()
    snapshot = make_snapshot()
    digest = hasher.hash(snapshot)

    assert hasher.validate(snapshot, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        TrustedKeyRegistrySnapshotHashError,
        match="hash mismatch",
    ):
        TrustedKeyRegistrySnapshotHasher().validate(
            make_snapshot(),
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
        TrustedKeyRegistrySnapshotHashError,
        match="expected_digest",
    ):
        TrustedKeyRegistrySnapshotHasher().validate(
            make_snapshot(),
            digest,
        )


def test_hasher_does_not_mutate_snapshot() -> None:
    snapshot = make_snapshot()
    original = snapshot

    TrustedKeyRegistrySnapshotHasher().hash(snapshot)

    assert snapshot == original


def test_snapshot_preserves_observer_only_boundary() -> None:
    snapshot = make_snapshot()

    assert snapshot.execution_requested is False
    assert snapshot.side_effects_permitted is False