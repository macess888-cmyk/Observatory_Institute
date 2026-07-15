import hashlib

import pytest

from models import PublicKeyMaterial
from services.public_key_fingerprint import (
    PublicKeyFingerprintError,
    PublicKeyFingerprintService,
)


PUBLIC_KEY_HEX = "a" * 64
PUBLIC_KEY_VALUE = f"ed25519:{PUBLIC_KEY_HEX}"


def test_service_generates_expected_sha256_fingerprint() -> None:
    expected = (
        "sha256:"
        + hashlib.sha256(
            bytes.fromhex(PUBLIC_KEY_HEX)
        ).hexdigest()
    )

    assert (
        PublicKeyFingerprintService().generate(
            PUBLIC_KEY_VALUE
        )
        == expected
    )


def test_service_is_deterministic() -> None:
    service = PublicKeyFingerprintService()

    first = service.generate(PUBLIC_KEY_VALUE)
    second = service.generate(PUBLIC_KEY_VALUE)

    assert first == second


def test_different_public_keys_produce_different_fingerprints() -> None:
    service = PublicKeyFingerprintService()

    first = service.generate(
        "ed25519:" + ("a" * 64)
    )
    second = service.generate(
        "ed25519:" + ("b" * 64)
    )

    assert first != second


def test_service_rejects_non_string_input() -> None:
    with pytest.raises(TypeError, match="string"):
        PublicKeyFingerprintService().generate(
            123  # type: ignore[arg-type]
        )


def test_service_rejects_empty_public_key_value() -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="must not be empty",
    ):
        PublicKeyFingerprintService().generate("")


def test_service_rejects_invalid_prefix() -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="ed25519 prefix",
    ):
        PublicKeyFingerprintService().generate(
            "rsa:" + ("a" * 64)
        )


def test_service_rejects_short_public_key() -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="64 hexadecimal characters",
    ):
        PublicKeyFingerprintService().generate(
            "ed25519:abc"
        )


def test_service_rejects_non_hexadecimal_public_key() -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="lowercase hexadecimal",
    ):
        PublicKeyFingerprintService().generate(
            "ed25519:" + ("z" * 64)
        )


def test_service_rejects_uppercase_hexadecimal() -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="lowercase hexadecimal",
    ):
        PublicKeyFingerprintService().generate(
            "ed25519:" + ("A" * 64)
        )


def test_service_validates_matching_fingerprint() -> None:
    service = PublicKeyFingerprintService()
    fingerprint = service.generate(PUBLIC_KEY_VALUE)

    assert service.validate(
        PUBLIC_KEY_VALUE,
        fingerprint,
    ) is True


def test_service_rejects_mismatched_fingerprint() -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="fingerprint mismatch",
    ):
        PublicKeyFingerprintService().validate(
            PUBLIC_KEY_VALUE,
            "sha256:" + ("9" * 64),
        )


@pytest.mark.parametrize(
    "fingerprint",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
        "sha256:" + ("A" * 64),
    ],
)
def test_service_rejects_invalid_expected_fingerprint(
    fingerprint: str,
) -> None:
    with pytest.raises(
        PublicKeyFingerprintError,
        match="expected_fingerprint",
    ):
        PublicKeyFingerprintService().validate(
            PUBLIC_KEY_VALUE,
            fingerprint,
        )


def test_service_validates_public_key_material() -> None:
    fingerprint = PublicKeyFingerprintService().generate(
        PUBLIC_KEY_VALUE
    )

    material = PublicKeyMaterial(
        material_id="PKM-001",
        key_id="KEY-001",
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        algorithm="ED25519",
        encoding="HEX",
        public_key_value=PUBLIC_KEY_VALUE,
        public_key_fingerprint=fingerprint,
        created_at=__import__("datetime").datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        valid_from=__import__("datetime").datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        valid_until=__import__("datetime").datetime(
            2027,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    assert (
        PublicKeyFingerprintService().validate_material(
            material
        )
        is True
    )


def test_service_rejects_material_fingerprint_mismatch() -> None:
    material = PublicKeyMaterial(
        material_id="PKM-001",
        key_id="KEY-001",
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        algorithm="ED25519",
        encoding="HEX",
        public_key_value=PUBLIC_KEY_VALUE,
        public_key_fingerprint="sha256:" + ("9" * 64),
        created_at=__import__("datetime").datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        valid_from=__import__("datetime").datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        valid_until=__import__("datetime").datetime(
            2027,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    with pytest.raises(
        PublicKeyFingerprintError,
        match="fingerprint mismatch",
    ):
        PublicKeyFingerprintService().validate_material(
            material
        )


def test_service_rejects_non_material_input() -> None:
    with pytest.raises(TypeError, match="PublicKeyMaterial"):
        PublicKeyFingerprintService().validate_material(
            "PKM-001"  # type: ignore[arg-type]
        )


def test_service_does_not_mutate_material() -> None:
    fingerprint = PublicKeyFingerprintService().generate(
        PUBLIC_KEY_VALUE
    )

    material = PublicKeyMaterial(
        material_id="PKM-001",
        key_id="KEY-001",
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        algorithm="ED25519",
        encoding="HEX",
        public_key_value=PUBLIC_KEY_VALUE,
        public_key_fingerprint=fingerprint,
        created_at=__import__("datetime").datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        valid_from=__import__("datetime").datetime(
            2026,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        valid_until=__import__("datetime").datetime(
            2027,
            7,
            15,
            12,
            0,
            tzinfo=__import__("datetime").timezone.utc,
        ),
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=False,
        execution_requested=False,
        side_effects_permitted=False,
    )
    original = material

    PublicKeyFingerprintService().validate_material(
        material
    )

    assert material == original