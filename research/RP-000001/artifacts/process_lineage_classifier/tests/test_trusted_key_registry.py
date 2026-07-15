from datetime import datetime, timezone

import pytest

from models import PublicKeyMaterial
from services.public_key_fingerprint import (
    PublicKeyFingerprintService,
)
from services.trusted_key_registry import (
    TrustedKeyRegistry,
    TrustedKeyRegistryError,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
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
    material_id: str = "PKM-001",
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    public_key_value: str = PUBLIC_KEY_VALUE_001,
    public_key_fingerprint: str | None = None,
    issuer_id: str = "OBSERVATORY-INSTITUTE",
    revoked: bool = False,
) -> PublicKeyMaterial:
    fingerprint = (
        PublicKeyFingerprintService().generate(
            public_key_value
        )
        if public_key_fingerprint is None
        else public_key_fingerprint
    )

    return PublicKeyMaterial(
        material_id=material_id,
        key_id=key_id,
        owner_id=owner_id,
        algorithm="ED25519",
        encoding="HEX",
        public_key_value=public_key_value,
        public_key_fingerprint=fingerprint,
        created_at=CREATED_AT,
        valid_from=CREATED_AT,
        valid_until=VALID_UNTIL,
        issuer_id=issuer_id,
        revoked=revoked,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_registry_starts_empty() -> None:
    registry = TrustedKeyRegistry()

    assert registry.count() == 0
    assert registry.list_key_ids() == ()


def test_registry_registers_public_key_material() -> None:
    registry = TrustedKeyRegistry()
    material = make_material()

    assert registry.register(material) is True
    assert registry.count() == 1
    assert registry.get("KEY-001") == material


def test_registry_rejects_non_material_input() -> None:
    with pytest.raises(TypeError, match="PublicKeyMaterial"):
        TrustedKeyRegistry().register(
            "PKM-001"  # type: ignore[arg-type]
        )


def test_registry_rejects_revoked_material() -> None:
    with pytest.raises(
        TrustedKeyRegistryError,
        match="[Rr]evoked",
    ):
        TrustedKeyRegistry().register(
            make_material(revoked=True)
        )


def test_registry_rejects_duplicate_key_identity() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())

    with pytest.raises(
        TrustedKeyRegistryError,
        match="duplicate key identity",
    ):
        registry.register(
            make_material(
                material_id="PKM-002",
                public_key_value=PUBLIC_KEY_VALUE_002,
            )
        )


def test_registry_rejects_duplicate_fingerprint() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())

    duplicate = make_material(
        material_id="PKM-002",
        key_id="KEY-002",
        public_key_value=PUBLIC_KEY_VALUE_002,
        public_key_fingerprint=FINGERPRINT_001,
    )

    with pytest.raises(
        TrustedKeyRegistryError,
        match="fingerprint validation",
    ):
        registry.register(duplicate)


def test_registry_rejects_duplicate_material_identity() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())

    with pytest.raises(
        TrustedKeyRegistryError,
        match="duplicate material identity",
    ):
        registry.register(
            make_material(
                key_id="KEY-002",
                public_key_value=PUBLIC_KEY_VALUE_002,
            )
        )


def test_registry_returns_key_by_identity() -> None:
    registry = TrustedKeyRegistry()
    material = make_material()
    registry.register(material)

    assert registry.get("KEY-001") == material


def test_registry_rejects_unknown_key_identity() -> None:
    with pytest.raises(
        TrustedKeyRegistryError,
        match="unknown key identity",
    ):
        TrustedKeyRegistry().get("KEY-999")


def test_registry_rejects_empty_key_identity_lookup() -> None:
    with pytest.raises(
        TrustedKeyRegistryError,
        match="key_id",
    ):
        TrustedKeyRegistry().get("")


def test_registry_checks_membership() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())

    assert registry.contains("KEY-001") is True
    assert registry.contains("KEY-999") is False


def test_registry_rejects_empty_membership_key_identity() -> None:
    with pytest.raises(
        TrustedKeyRegistryError,
        match="key_id",
    ):
        TrustedKeyRegistry().contains("")


def test_registry_lists_key_ids_in_registration_order() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())
    registry.register(
        make_material(
            material_id="PKM-002",
            key_id="KEY-002",
            public_key_value=PUBLIC_KEY_VALUE_002,
        )
    )

    assert registry.list_key_ids() == (
        "KEY-001",
        "KEY-002",
    )


def test_registry_lists_materials_in_registration_order() -> None:
    registry = TrustedKeyRegistry()
    first = make_material()
    second = make_material(
        material_id="PKM-002",
        key_id="KEY-002",
        public_key_value=PUBLIC_KEY_VALUE_002,
    )
    registry.register(first)
    registry.register(second)

    assert registry.list_materials() == (
        first,
        second,
    )


def test_registry_validates_expected_owner() -> None:
    registry = TrustedKeyRegistry(
        expected_owner_id="PROCESS-LINEAGE-CLASSIFIER"
    )

    assert registry.register(make_material()) is True


def test_registry_rejects_owner_mismatch() -> None:
    registry = TrustedKeyRegistry(
        expected_owner_id="PROCESS-LINEAGE-CLASSIFIER"
    )

    with pytest.raises(
        TrustedKeyRegistryError,
        match="owner identity",
    ):
        registry.register(
            make_material(owner_id="OTHER-OWNER")
        )


def test_registry_validates_expected_issuer() -> None:
    registry = TrustedKeyRegistry(
        expected_issuer_id="OBSERVATORY-INSTITUTE"
    )

    assert registry.register(make_material()) is True


def test_registry_rejects_issuer_mismatch() -> None:
    registry = TrustedKeyRegistry(
        expected_issuer_id="OBSERVATORY-INSTITUTE"
    )

    with pytest.raises(
        TrustedKeyRegistryError,
        match="issuer identity",
    ):
        registry.register(
            make_material(issuer_id="OTHER-ISSUER")
        )


def test_registry_rejects_empty_expected_owner() -> None:
    with pytest.raises(
        TrustedKeyRegistryError,
        match="expected_owner_id",
    ):
        TrustedKeyRegistry(expected_owner_id="")


def test_registry_rejects_empty_expected_issuer() -> None:
    with pytest.raises(
        TrustedKeyRegistryError,
        match="expected_issuer_id",
    ):
        TrustedKeyRegistry(expected_issuer_id="")


def test_registry_snapshot_is_immutable() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())

    snapshot = registry.snapshot()

    assert isinstance(snapshot, tuple)

    with pytest.raises(AttributeError):
        snapshot.append(make_material())  # type: ignore[attr-defined]


def test_registry_does_not_mutate_material() -> None:
    registry = TrustedKeyRegistry()
    material = make_material()
    original = material

    registry.register(material)

    assert material == original


def test_registry_preserves_observer_only_boundary() -> None:
    registry = TrustedKeyRegistry()
    registry.register(make_material())

    assert registry.execution_requested is False
    assert registry.side_effects_permitted is False
