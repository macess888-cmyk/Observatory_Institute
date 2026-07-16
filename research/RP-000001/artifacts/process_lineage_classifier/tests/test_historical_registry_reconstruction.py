from datetime import datetime, timezone

import pytest

from models import (
    PublicKeyMaterial,
    RegistryVersionRecord,
    TrustedKeyRegistrySnapshot,
)
from services.historical_registry_reconstruction import (
    HistoricalRegistryReconstructionError,
    HistoricalRegistryReconstructionService,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)
from services.trusted_key_registry_snapshot_hasher import (
    TrustedKeyRegistrySnapshotHasher,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
SNAPSHOT_001_AT = datetime(2026, 7, 15, 12, 30, tzinfo=timezone.utc)
SNAPSHOT_002_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
SNAPSHOT_003_AT = datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)

PUBLIC_KEY_VALUE_001 = "ed25519:" + ("a" * 64)
PUBLIC_KEY_VALUE_002 = "ed25519:" + ("b" * 64)
PUBLIC_KEY_VALUE_003 = "ed25519:" + ("c" * 64)

FINGERPRINT_001 = PublicKeyFingerprintService().generate(
    PUBLIC_KEY_VALUE_001
)
FINGERPRINT_002 = PublicKeyFingerprintService().generate(
    PUBLIC_KEY_VALUE_002
)
FINGERPRINT_003 = PublicKeyFingerprintService().generate(
    PUBLIC_KEY_VALUE_003
)

ADMISSION_RECEIPT_DIGEST = "sha256:" + ("4" * 64)
REMOVAL_RECEIPT_DIGEST = "sha256:" + ("5" * 64)


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


def make_snapshots() -> tuple[
    TrustedKeyRegistrySnapshot,
    TrustedKeyRegistrySnapshot,
    TrustedKeyRegistrySnapshot,
]:
    key_001 = make_material(
        material_id="PKM-001",
        key_id="KEY-001",
        public_key_value=PUBLIC_KEY_VALUE_001,
        public_key_fingerprint=FINGERPRINT_001,
    )
    key_002 = make_material(
        material_id="PKM-002",
        key_id="KEY-002",
        public_key_value=PUBLIC_KEY_VALUE_002,
        public_key_fingerprint=FINGERPRINT_002,
    )
    key_003 = make_material(
        material_id="PKM-003",
        key_id="KEY-003",
        public_key_value=PUBLIC_KEY_VALUE_003,
        public_key_fingerprint=FINGERPRINT_003,
    )

    snapshot_001 = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-001",
        registry_id="TKR-001",
        registry_version="1.0.0",
        materials=(key_001, key_002),
        captured_at=SNAPSHOT_001_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    snapshot_002 = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-002",
        registry_id="TKR-001",
        registry_version="1.1.0",
        materials=(key_001, key_002, key_003),
        captured_at=SNAPSHOT_002_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    snapshot_003 = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-003",
        registry_id="TKR-001",
        registry_version="1.2.0",
        materials=(key_001, key_002),
        captured_at=SNAPSHOT_003_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    return snapshot_001, snapshot_002, snapshot_003


def make_records(
    snapshots: tuple[
        TrustedKeyRegistrySnapshot,
        TrustedKeyRegistrySnapshot,
        TrustedKeyRegistrySnapshot,
    ],
) -> tuple[RegistryVersionRecord, RegistryVersionRecord]:
    snapshot_001, snapshot_002, snapshot_003 = snapshots
    hasher = TrustedKeyRegistrySnapshotHasher()

    record_002 = RegistryVersionRecord(
        record_id="RVR-002",
        registry_id="TKR-001",
        registry_version="1.1.0",
        previous_registry_version="1.0.0",
        snapshot_id=snapshot_002.snapshot_id,
        snapshot_digest=hasher.hash(snapshot_002),
        previous_snapshot_id=snapshot_001.snapshot_id,
        previous_snapshot_digest=hasher.hash(snapshot_001),
        transition_type="ADMISSION",
        transition_receipt_id="TKAR-001",
        transition_receipt_digest=ADMISSION_RECEIPT_DIGEST,
        recorded_at=SNAPSHOT_002_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    record_003 = RegistryVersionRecord(
        record_id="RVR-003",
        registry_id="TKR-001",
        registry_version="1.2.0",
        previous_registry_version="1.1.0",
        snapshot_id=snapshot_003.snapshot_id,
        snapshot_digest=hasher.hash(snapshot_003),
        previous_snapshot_id=snapshot_002.snapshot_id,
        previous_snapshot_digest=hasher.hash(snapshot_002),
        transition_type="REMOVAL",
        transition_receipt_id="TKRR-001",
        transition_receipt_digest=REMOVAL_RECEIPT_DIGEST,
        recorded_at=SNAPSHOT_003_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    return record_002, record_003


def make_fixture():
    snapshots = make_snapshots()
    return snapshots, make_records(snapshots)


def test_service_reconstructs_requested_version() -> None:
    snapshots, records = make_fixture()

    reconstructed = HistoricalRegistryReconstructionService().reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.1.0",
        snapshots=snapshots,
        version_records=records,
    )

    assert reconstructed == snapshots[1]
    assert tuple(m.key_id for m in reconstructed.materials) == (
        "KEY-001",
        "KEY-002",
        "KEY-003",
    )


def test_service_reconstructs_latest_version() -> None:
    snapshots, records = make_fixture()

    reconstructed = HistoricalRegistryReconstructionService().reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.2.0",
        snapshots=snapshots,
        version_records=records,
    )

    assert reconstructed == snapshots[2]
    assert tuple(m.key_id for m in reconstructed.materials) == (
        "KEY-001",
        "KEY-002",
    )


def test_removed_key_remains_present_in_historical_snapshot() -> None:
    snapshots, records = make_fixture()
    service = HistoricalRegistryReconstructionService()

    historical = service.reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.1.0",
        snapshots=snapshots,
        version_records=records,
    )
    current = service.reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.2.0",
        snapshots=snapshots,
        version_records=records,
    )

    assert "KEY-003" in tuple(m.key_id for m in historical.materials)
    assert "KEY-003" not in tuple(m.key_id for m in current.materials)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("registry_id", ""),
        ("target_registry_version", ""),
    ],
)
def test_service_rejects_empty_identity(
    field_name: str,
    value: str,
) -> None:
    snapshots, records = make_fixture()
    arguments = {
        "registry_id": "TKR-001",
        "target_registry_version": "1.1.0",
        "snapshots": snapshots,
        "version_records": records,
    }
    arguments[field_name] = value

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match=field_name,
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            **arguments
        )


def test_service_rejects_non_tuple_snapshots() -> None:
    _, records = make_fixture()

    with pytest.raises(TypeError, match="snapshots"):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=[],  # type: ignore[arg-type]
            version_records=records,
        )


def test_service_rejects_non_tuple_version_records() -> None:
    snapshots, _ = make_fixture()

    with pytest.raises(TypeError, match="version_records"):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=[],  # type: ignore[arg-type]
        )


def test_service_rejects_empty_snapshots() -> None:
    _, records = make_fixture()

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="snapshots",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=(),
            version_records=records,
        )


def test_service_rejects_non_snapshot_member() -> None:
    _, records = make_fixture()

    with pytest.raises(
        TypeError,
        match="TrustedKeyRegistrySnapshot",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=("TKRS-001",),  # type: ignore[arg-type]
            version_records=records,
        )


def test_service_rejects_non_record_member() -> None:
    snapshots, _ = make_fixture()

    with pytest.raises(
        TypeError,
        match="RegistryVersionRecord",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=("RVR-001",),  # type: ignore[arg-type]
        )


def test_service_rejects_unknown_target_version() -> None:
    snapshots, records = make_fixture()

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="target registry version",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="9.9.9",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_rejects_registry_identity_mismatch() -> None:
    snapshots, records = make_fixture()
    object.__setattr__(snapshots[1], "registry_id", "TKR-999")

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="registry identity",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_rejects_duplicate_snapshot_version() -> None:
    snapshots, records = make_fixture()
    duplicate = TrustedKeyRegistrySnapshot(
        snapshot_id="TKRS-999",
        registry_id="TKR-001",
        registry_version="1.1.0",
        materials=snapshots[1].materials,
        captured_at=SNAPSHOT_002_AT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        execution_requested=False,
        side_effects_permitted=False,
    )

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="duplicate snapshot version",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots + (duplicate,),
            version_records=records,
        )


def test_service_rejects_duplicate_version_record() -> None:
    snapshots, records = make_fixture()

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="duplicate version record",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=records + (records[0],),
        )


def test_service_rejects_broken_version_chain() -> None:
    snapshots, records = make_fixture()
    object.__setattr__(
        records[1],
        "previous_registry_version",
        "1.0.0",
    )

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="version chain",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.2.0",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_rejects_snapshot_digest_mismatch() -> None:
    snapshots, records = make_fixture()
    object.__setattr__(
        records[0],
        "snapshot_digest",
        "sha256:" + ("9" * 64),
    )

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="snapshot digest",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_rejects_previous_snapshot_digest_mismatch() -> None:
    snapshots, records = make_fixture()
    object.__setattr__(
        records[0],
        "previous_snapshot_digest",
        "sha256:" + ("9" * 64),
    )

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="previous snapshot digest",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_rejects_snapshot_identity_mismatch() -> None:
    snapshots, records = make_fixture()
    object.__setattr__(records[0], "snapshot_id", "TKRS-999")

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="snapshot identity",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_rejects_previous_snapshot_identity_mismatch() -> None:
    snapshots, records = make_fixture()
    object.__setattr__(
        records[0],
        "previous_snapshot_id",
        "TKRS-999",
    )

    with pytest.raises(
        HistoricalRegistryReconstructionError,
        match="previous snapshot identity",
    ):
        HistoricalRegistryReconstructionService().reconstruct(
            registry_id="TKR-001",
            target_registry_version="1.1.0",
            snapshots=snapshots,
            version_records=records,
        )


def test_service_is_deterministic() -> None:
    snapshots, records = make_fixture()
    service = HistoricalRegistryReconstructionService()

    first = service.reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.1.0",
        snapshots=snapshots,
        version_records=records,
    )
    second = service.reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.1.0",
        snapshots=snapshots,
        version_records=records,
    )

    assert first == second


def test_service_does_not_mutate_inputs() -> None:
    snapshots, records = make_fixture()
    original_snapshots = snapshots
    original_records = records

    HistoricalRegistryReconstructionService().reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.1.0",
        snapshots=snapshots,
        version_records=records,
    )

    assert snapshots == original_snapshots
    assert records == original_records


def test_reconstructed_snapshot_preserves_observer_only_boundary() -> None:
    snapshots, records = make_fixture()

    reconstructed = HistoricalRegistryReconstructionService().reconstruct(
        registry_id="TKR-001",
        target_registry_version="1.1.0",
        snapshots=snapshots,
        version_records=records,
    )

    assert reconstructed.execution_requested is False
    assert reconstructed.side_effects_permitted is False