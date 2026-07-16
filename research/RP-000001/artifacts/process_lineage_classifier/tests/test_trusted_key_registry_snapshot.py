from datetime import datetime, timezone

import pytest

from models import (
    PublicKeyMaterial,
    TrustedKeyRegistrySnapshot,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)
from services.trusted_key_registry_snapshot_validator import (
    TrustedKeyRegistrySnapshotError,
    TrustedKeyRegistrySnapshotValidator,
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
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    issuer_id: str = "OBSERVATORY-INSTITUTE",
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
        owner_id=owner_id,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_snapshot() -> None:
    snapshot = make_snapshot()

    assert (
        TrustedKeyRegistrySnapshotValidator().validate(
            snapshot
        )
        is True
    )


def test_snapshot_is_immutable() -> None:
    snapshot = make_snapshot()

    with pytest.raises((AttributeError, TypeError)):
        snapshot.registry_version = "2.0.0"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "snapshot_id",
        "registry_id",
        "registry_version",
        "owner_id",
        "issuer_id",
    ],
)
def test_snapshot_rejects_empty_identity(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_snapshot(**{field_name: ""})


def test_snapshot_rejects_non_tuple_materials() -> None:
    with pytest.raises(TypeError, match="materials"):
        make_snapshot(
            materials=[]  # type: ignore[arg-type]
        )


def test_snapshot_rejects_empty_materials() -> None:
    with pytest.raises(ValueError, match="materials"):
        make_snapshot(materials=())


def test_snapshot_rejects_non_material_member() -> None:
    with pytest.raises(TypeError, match="PublicKeyMaterial"):
        make_snapshot(
            materials=(
                "PKM-001",  # type: ignore[arg-type]
            )
        )


def test_snapshot_rejects_duplicate_key_identity() -> None:
    first = make_material(
        material_id="PKM-001",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_001,
        public_key_fingerprint=FINGERPRINT_001,
    )
    second = make_material(
        material_id="PKM-002",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_002,
        public_key_fingerprint=FINGERPRINT_002,
    )

    with pytest.raises(ValueError, match="duplicate key identity"):
        make_snapshot(materials=(first, second))


def test_snapshot_rejects_duplicate_material_identity() -> None:
    first = make_material(
        material_id="PKM-001",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_001,
        public_key_fingerprint=FINGERPRINT_001,
    )
    second = make_material(
        material_id="PKM-001",
        key_id="KEY-002",
        public_key_value=PUBLIC_KEY_VALUE_002,
        public_key_fingerprint=FINGERPRINT_002,
    )

    with pytest.raises(
        ValueError,
        match="duplicate material identity",
    ):
        make_snapshot(materials=(first, second))


def test_snapshot_rejects_duplicate_fingerprint() -> None:
    first = make_material(
        material_id="PKM-001",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_001,
        public_key_fingerprint=FINGERPRINT_001,
    )
    second = make_material(
        material_id="PKM-002",
        key_id="KEY-002",
        public_key_value=PUBLIC_KEY_VALUE_002,
        public_key_fingerprint=FINGERPRINT_001,
    )

    with pytest.raises(
        ValueError,
        match="duplicate fingerprint",
    ):
        make_snapshot(materials=(first, second))


def test_snapshot_rejects_owner_mismatch() -> None:
    material = make_material(
        material_id="PKM-001",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_001,
        public_key_fingerprint=FINGERPRINT_001,
    )
    object.__setattr__(material, "owner_id", "OTHER-OWNER")

    with pytest.raises(ValueError, match="owner identity"):
        make_snapshot(materials=(material,))


def test_snapshot_rejects_issuer_mismatch() -> None:
    material = make_material(
        material_id="PKM-001",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_001,
        public_key_fingerprint=FINGERPRINT_001,
    )
    object.__setattr__(material, "issuer_id", "OTHER-ISSUER")

    with pytest.raises(ValueError, match="issuer identity"):
        make_snapshot(materials=(material,))


def test_snapshot_rejects_naive_captured_at() -> None:
    with pytest.raises(
        ValueError,
        match="captured_at.*timezone-aware",
    ):
        make_snapshot(
            captured_at=datetime(2026, 7, 15, 12, 30)
        )


def test_snapshot_rejects_capture_before_material_creation() -> None:
    with pytest.raises(ValueError, match="captured_at"):
        make_snapshot(
            captured_at=datetime(
                2026,
                7,
                15,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            )
        )


def test_validator_rejects_non_snapshot_input() -> None:
    with pytest.raises(
        TypeError,
        match="TrustedKeyRegistrySnapshot",
    ):
        TrustedKeyRegistrySnapshotValidator().validate(
            "TKRS-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    snapshot = make_snapshot()

    assert (
        TrustedKeyRegistrySnapshotValidator().validate(
            snapshot,
            expected_registry_id="TKR-001",
            expected_registry_version="1.0.0",
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_issuer_id="OBSERVATORY-INSTITUTE",
            expected_material_count=2,
        )
        is True
    )


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
            "expected_owner_id",
            "OTHER-OWNER",
            "owner identity",
        ),
        (
            "expected_issuer_id",
            "OTHER-ISSUER",
            "issuer identity",
        ),
        (
            "expected_material_count",
            99,
            "material count",
        ),
    ],
)
def test_validator_rejects_reference_mismatch(
    field_name: str,
    value: object,
    error_match: str,
) -> None:
    arguments: dict[str, object] = {
        "expected_registry_id": "TKR-001",
        "expected_registry_version": "1.0.0",
        "expected_owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "expected_issuer_id": "OBSERVATORY-INSTITUTE",
        "expected_material_count": 2,
    }
    arguments[field_name] = value

    with pytest.raises(
        TrustedKeyRegistrySnapshotError,
        match=error_match,
    ):
        TrustedKeyRegistrySnapshotValidator().validate(
            make_snapshot(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        TrustedKeyRegistrySnapshotError,
        match="complete expected reference set",
    ):
        TrustedKeyRegistrySnapshotValidator().validate(
            make_snapshot(),
            expected_registry_id="TKR-001",
        )


def test_validator_does_not_mutate_snapshot() -> None:
    snapshot = make_snapshot()
    original = snapshot

    TrustedKeyRegistrySnapshotValidator().validate(snapshot)

    assert snapshot == original


def test_snapshot_preserves_material_order() -> None:
    snapshot = make_snapshot()

    assert tuple(
        material.key_id
        for material in snapshot.materials
    ) == (
        "KEY-001",
        "KEY-002",
    )


def test_snapshot_preserves_observer_only_boundary() -> None:
    snapshot = make_snapshot()

    assert snapshot.execution_requested is False
    assert snapshot.side_effects_permitted is False