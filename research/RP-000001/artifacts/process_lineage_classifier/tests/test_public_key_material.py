from datetime import datetime, timezone

import pytest

from models import PublicKeyMaterial
from services.public_key_material_validator import (
    PublicKeyMaterialError,
    PublicKeyMaterialValidator,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_FROM = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2027, 7, 15, 12, 0, tzinfo=timezone.utc)

PUBLIC_KEY_VALUE = "ed25519:" + ("a" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("1" * 64)


def make_public_key(
    *,
    material_id: str = "PKM-001",
    key_id: str = "KEY-001",
    owner_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    algorithm: str = "ED25519",
    encoding: str = "HEX",
    public_key_value: str = PUBLIC_KEY_VALUE,
    public_key_fingerprint: str = PUBLIC_KEY_FINGERPRINT,
    created_at: datetime = CREATED_AT,
    valid_from: datetime = VALID_FROM,
    valid_until: datetime = VALID_UNTIL,
    issuer_id: str = "OBSERVATORY-INSTITUTE",
    revoked: bool = False,
) -> PublicKeyMaterial:
    return PublicKeyMaterial(
        material_id=material_id,
        key_id=key_id,
        owner_id=owner_id,
        algorithm=algorithm,
        encoding=encoding,
        public_key_value=public_key_value,
        public_key_fingerprint=public_key_fingerprint,
        created_at=created_at,
        valid_from=valid_from,
        valid_until=valid_until,
        issuer_id=issuer_id,
        revoked=revoked,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_public_key_material() -> None:
    material = make_public_key()

    assert PublicKeyMaterialValidator().validate(material) is True


def test_public_key_material_is_immutable() -> None:
    material = make_public_key()

    with pytest.raises((AttributeError, TypeError)):
        material.revoked = True  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "material_id",
        "key_id",
        "owner_id",
        "algorithm",
        "encoding",
        "public_key_value",
        "issuer_id",
    ],
)
def test_public_key_material_rejects_empty_value(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        make_public_key(**{field_name: ""})


def test_public_key_material_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="algorithm"):
        make_public_key(algorithm="RSA")


def test_public_key_material_rejects_unsupported_encoding() -> None:
    with pytest.raises(ValueError, match="encoding"):
        make_public_key(encoding="BASE64")


def test_public_key_material_rejects_invalid_value_prefix() -> None:
    with pytest.raises(ValueError, match="public_key_value"):
        make_public_key(public_key_value="rsa:invalid")


def test_public_key_material_rejects_short_value() -> None:
    with pytest.raises(ValueError, match="public_key_value"):
        make_public_key(public_key_value="ed25519:abc")


def test_public_key_material_rejects_non_hex_value() -> None:
    with pytest.raises(ValueError, match="public_key_value"):
        make_public_key(
            public_key_value="ed25519:" + ("z" * 64)
        )


@pytest.mark.parametrize(
    "fingerprint",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
    ],
)
def test_public_key_material_rejects_invalid_fingerprint(
    fingerprint: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="public_key_fingerprint",
    ):
        make_public_key(
            public_key_fingerprint=fingerprint,
        )


def test_public_key_material_rejects_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="created_at.*timezone-aware",
    ):
        make_public_key(
            created_at=datetime(2026, 7, 15, 12, 0),
        )


def test_public_key_material_rejects_naive_valid_from() -> None:
    with pytest.raises(
        ValueError,
        match="valid_from.*timezone-aware",
    ):
        make_public_key(
            valid_from=datetime(2026, 7, 15, 12, 0),
        )


def test_public_key_material_rejects_naive_valid_until() -> None:
    with pytest.raises(
        ValueError,
        match="valid_until.*timezone-aware",
    ):
        make_public_key(
            valid_until=datetime(2027, 7, 15, 12, 0),
        )


def test_public_key_material_rejects_valid_from_before_creation() -> None:
    with pytest.raises(ValueError, match="valid_from"):
        make_public_key(
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


def test_public_key_material_rejects_invalid_valid_until() -> None:
    with pytest.raises(ValueError, match="valid_until"):
        make_public_key(valid_until=VALID_FROM)


def test_public_key_material_rejects_non_boolean_revoked() -> None:
    with pytest.raises(TypeError, match="revoked"):
        make_public_key(
            revoked="false",  # type: ignore[arg-type]
        )


def test_validator_rejects_non_material_input() -> None:
    with pytest.raises(TypeError, match="PublicKeyMaterial"):
        PublicKeyMaterialValidator().validate(
            "PKM-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    material = make_public_key()

    assert (
        PublicKeyMaterialValidator().validate(
            material,
            expected_key_id="KEY-001",
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
            expected_encoding="HEX",
            expected_fingerprint=PUBLIC_KEY_FINGERPRINT,
            expected_issuer_id="OBSERVATORY-INSTITUTE",
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
            "expected_algorithm",
            "OTHER",
            "algorithm",
        ),
        (
            "expected_encoding",
            "OTHER",
            "encoding",
        ),
        (
            "expected_fingerprint",
            "sha256:" + ("9" * 64),
            "fingerprint",
        ),
        (
            "expected_issuer_id",
            "OTHER-ISSUER",
            "issuer identity",
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
        "expected_algorithm": "ED25519",
        "expected_encoding": "HEX",
        "expected_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "expected_issuer_id": "OBSERVATORY-INSTITUTE",
    }
    arguments[expected_field] = expected_value

    with pytest.raises(
        PublicKeyMaterialError,
        match=error_match,
    ):
        PublicKeyMaterialValidator().validate(
            make_public_key(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        PublicKeyMaterialError,
        match="complete expected reference set",
    ):
        PublicKeyMaterialValidator().validate(
            make_public_key(),
            expected_key_id="KEY-001",
        )


def test_validator_rejects_revoked_public_key_material() -> None:
    with pytest.raises(
        PublicKeyMaterialError,
        match="revoked",
    ):
        PublicKeyMaterialValidator().validate(
            make_public_key(revoked=True)
        )


def test_validator_does_not_mutate_material() -> None:
    material = make_public_key()
    original = material

    PublicKeyMaterialValidator().validate(material)

    assert material == original


def test_public_key_material_preserves_observer_only_boundary() -> None:
    material = make_public_key()

    assert material.execution_requested is False
    assert material.side_effects_permitted is False