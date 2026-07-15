from datetime import datetime, timezone

import pytest

from models import (
    KeyRevocationRecord,
    KeyRotationRecord,
    SigningKeyIdentity,
)
from services.key_lineage_validator import (
    KeyLineageError,
    KeyLineageValidator,
)


BASE_TIME = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

FINGERPRINT_001 = "sha256:" + ("1" * 64)
FINGERPRINT_002 = "sha256:" + ("2" * 64)
FINGERPRINT_003 = "sha256:" + ("3" * 64)


def make_key(
    *,
    key_id: str,
    fingerprint: str,
    created_at: datetime,
    valid_from: datetime,
    valid_until: datetime,
    revoked: bool = False,
) -> SigningKeyIdentity:
    return SigningKeyIdentity(
        key_id=key_id,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        algorithm="ED25519",
        public_key_fingerprint=fingerprint,
        created_at=created_at,
        valid_from=valid_from,
        valid_until=valid_until,
        issuer_id="OBSERVATORY-INSTITUTE",
        revoked=revoked,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_rotation(
    *,
    rotation_id: str,
    previous_key_id: str,
    previous_fingerprint: str,
    new_key_id: str,
    new_fingerprint: str,
    rotated_at: datetime,
) -> KeyRotationRecord:
    return KeyRotationRecord(
        rotation_id=rotation_id,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        previous_key_id=previous_key_id,
        previous_key_fingerprint=previous_fingerprint,
        new_key_id=new_key_id,
        new_key_fingerprint=new_fingerprint,
        algorithm="ED25519",
        rotated_at=rotated_at,
        rotated_by="OBSERVATORY-INSTITUTE",
        reason="Scheduled key rotation.",
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_revocation(
    *,
    revocation_id: str,
    key_id: str,
    fingerprint: str,
    revoked_at: datetime,
) -> KeyRevocationRecord:
    return KeyRevocationRecord(
        revocation_id=revocation_id,
        key_id=key_id,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        key_fingerprint=fingerprint,
        algorithm="ED25519",
        revoked_at=revoked_at,
        revoked_by="OBSERVATORY-INSTITUTE",
        reason="Key retired after rotation.",
        permanent=True,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_valid_lineage() -> tuple[
    tuple[SigningKeyIdentity, ...],
    tuple[KeyRotationRecord, ...],
    tuple[KeyRevocationRecord, ...],
]:
    key_001 = make_key(
        key_id="KEY-001",
        fingerprint=FINGERPRINT_001,
        created_at=BASE_TIME,
        valid_from=BASE_TIME,
        valid_until=datetime(
            2026,
            8,
            15,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        revoked=True,
    )
    key_002 = make_key(
        key_id="KEY-002",
        fingerprint=FINGERPRINT_002,
        created_at=datetime(
            2026,
            8,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        valid_from=datetime(
            2026,
            8,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        valid_until=datetime(
            2026,
            9,
            15,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        revoked=True,
    )
    key_003 = make_key(
        key_id="KEY-003",
        fingerprint=FINGERPRINT_003,
        created_at=datetime(
            2026,
            9,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        valid_from=datetime(
            2026,
            9,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        valid_until=datetime(
            2027,
            9,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        revoked=False,
    )

    rotation_001 = make_rotation(
        rotation_id="KRR-001",
        previous_key_id="KEY-001",
        previous_fingerprint=FINGERPRINT_001,
        new_key_id="KEY-002",
        new_fingerprint=FINGERPRINT_002,
        rotated_at=datetime(
            2026,
            8,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )
    rotation_002 = make_rotation(
        rotation_id="KRR-002",
        previous_key_id="KEY-002",
        previous_fingerprint=FINGERPRINT_002,
        new_key_id="KEY-003",
        new_fingerprint=FINGERPRINT_003,
        rotated_at=datetime(
            2026,
            9,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    revocation_001 = make_revocation(
        revocation_id="KRV-001",
        key_id="KEY-001",
        fingerprint=FINGERPRINT_001,
        revoked_at=datetime(
            2026,
            8,
            1,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )
    revocation_002 = make_revocation(
        revocation_id="KRV-002",
        key_id="KEY-002",
        fingerprint=FINGERPRINT_002,
        revoked_at=datetime(
            2026,
            9,
            1,
            12,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )

    return (
        (key_001, key_002, key_003),
        (rotation_001, rotation_002),
        (revocation_001, revocation_002),
    )


def test_validator_accepts_valid_key_lineage() -> None:
    keys, rotations, revocations = make_valid_lineage()

    assert KeyLineageValidator().validate(
        keys=keys,
        rotations=rotations,
        revocations=revocations,
        expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
        expected_algorithm="ED25519",
    ) is True


def test_validator_rejects_non_tuple_keys() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(TypeError, match="keys must be a tuple"):
        KeyLineageValidator().validate(
            keys=list(keys),  # type: ignore[arg-type]
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_empty_key_set() -> None:
    _, rotations, revocations = make_valid_lineage()

    with pytest.raises(KeyLineageError, match="at least one key"):
        KeyLineageValidator().validate(
            keys=(),
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_non_key_member() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(TypeError, match="SigningKeyIdentity"):
        KeyLineageValidator().validate(
            keys=(keys[0], "KEY-002"),  # type: ignore[arg-type]
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_duplicate_key_identity() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(KeyLineageError, match="duplicate key identity"):
        KeyLineageValidator().validate(
            keys=(keys[0], keys[0], keys[2]),
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_duplicate_key_fingerprint() -> None:
    keys, rotations, revocations = make_valid_lineage()
    duplicate = make_key(
        key_id="KEY-999",
        fingerprint=FINGERPRINT_001,
        created_at=keys[1].created_at,
        valid_from=keys[1].valid_from,
        valid_until=keys[1].valid_until,
        revoked=True,
    )

    with pytest.raises(
        KeyLineageError,
        match="duplicate key fingerprint",
    ):
        KeyLineageValidator().validate(
            keys=(keys[0], duplicate, keys[2]),
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_owner_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(KeyLineageError, match="owner identity"):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="OTHER-OWNER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_algorithm_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(KeyLineageError, match="algorithm"):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="OTHER",
        )


def test_validator_rejects_missing_rotation() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(KeyLineageError, match="rotation count"):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=(rotations[0],),
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_rotation_previous_key_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_rotation(
        rotation_id="KRR-001",
        previous_key_id="KEY-999",
        previous_fingerprint=FINGERPRINT_001,
        new_key_id="KEY-002",
        new_fingerprint=FINGERPRINT_002,
        rotated_at=rotations[0].rotated_at,
    )

    with pytest.raises(
        KeyLineageError,
        match="previous key identity",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=(broken, rotations[1]),
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_rotation_new_key_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_rotation(
        rotation_id="KRR-001",
        previous_key_id="KEY-001",
        previous_fingerprint=FINGERPRINT_001,
        new_key_id="KEY-999",
        new_fingerprint=FINGERPRINT_002,
        rotated_at=rotations[0].rotated_at,
    )

    with pytest.raises(
        KeyLineageError,
        match="new key identity",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=(broken, rotations[1]),
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_rotation_fingerprint_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_rotation(
        rotation_id="KRR-001",
        previous_key_id="KEY-001",
        previous_fingerprint=FINGERPRINT_003,
        new_key_id="KEY-002",
        new_fingerprint=FINGERPRINT_002,
        rotated_at=rotations[0].rotated_at,
    )

    with pytest.raises(
        KeyLineageError,
        match="previous key fingerprint",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=(broken, rotations[1]),
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_rotation_before_new_key_creation() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_rotation(
        rotation_id="KRR-001",
        previous_key_id="KEY-001",
        previous_fingerprint=FINGERPRINT_001,
        new_key_id="KEY-002",
        new_fingerprint=FINGERPRINT_002,
        rotated_at=datetime(
            2026,
            7,
            31,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        KeyLineageError,
        match="before new key creation",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=(broken, rotations[1]),
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_missing_revocation() -> None:
    keys, rotations, revocations = make_valid_lineage()

    with pytest.raises(KeyLineageError, match="revocation count"):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=rotations,
            revocations=(revocations[0],),
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_revocation_key_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_revocation(
        revocation_id="KRV-001",
        key_id="KEY-999",
        fingerprint=FINGERPRINT_001,
        revoked_at=revocations[0].revoked_at,
    )

    with pytest.raises(
        KeyLineageError,
        match="revocation key identity",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=rotations,
            revocations=(broken, revocations[1]),
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_revocation_fingerprint_mismatch() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_revocation(
        revocation_id="KRV-001",
        key_id="KEY-001",
        fingerprint=FINGERPRINT_003,
        revoked_at=revocations[0].revoked_at,
    )

    with pytest.raises(
        KeyLineageError,
        match="revocation key fingerprint",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=rotations,
            revocations=(broken, revocations[1]),
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_revocation_before_rotation() -> None:
    keys, rotations, revocations = make_valid_lineage()
    broken = make_revocation(
        revocation_id="KRV-001",
        key_id="KEY-001",
        fingerprint=FINGERPRINT_001,
        revoked_at=datetime(
            2026,
            8,
            1,
            11,
            59,
            59,
            tzinfo=timezone.utc,
        ),
    )

    with pytest.raises(
        KeyLineageError,
        match="before rotation",
    ):
        KeyLineageValidator().validate(
            keys=keys,
            rotations=rotations,
            revocations=(broken, revocations[1]),
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_retired_key_not_marked_revoked() -> None:
    keys, rotations, revocations = make_valid_lineage()
    unrevoked = make_key(
        key_id="KEY-001",
        fingerprint=FINGERPRINT_001,
        created_at=keys[0].created_at,
        valid_from=keys[0].valid_from,
        valid_until=keys[0].valid_until,
        revoked=False,
    )

    with pytest.raises(
        KeyLineageError,
        match="retired key must be marked revoked",
    ):
        KeyLineageValidator().validate(
            keys=(unrevoked, keys[1], keys[2]),
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_rejects_active_key_marked_revoked() -> None:
    keys, rotations, revocations = make_valid_lineage()
    revoked_active = make_key(
        key_id="KEY-003",
        fingerprint=FINGERPRINT_003,
        created_at=keys[2].created_at,
        valid_from=keys[2].valid_from,
        valid_until=keys[2].valid_until,
        revoked=True,
    )

    with pytest.raises(
        KeyLineageError,
        match="active key must not be revoked",
    ):
        KeyLineageValidator().validate(
            keys=(keys[0], keys[1], revoked_active),
            rotations=rotations,
            revocations=revocations,
            expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
            expected_algorithm="ED25519",
        )


def test_validator_does_not_mutate_inputs() -> None:
    keys, rotations, revocations = make_valid_lineage()
    original = (keys, rotations, revocations)

    KeyLineageValidator().validate(
        keys=keys,
        rotations=rotations,
        revocations=revocations,
        expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
        expected_algorithm="ED25519",
    )

    assert (keys, rotations, revocations) == original


def test_key_lineage_preserves_observer_only_boundary() -> None:
    keys, rotations, revocations = make_valid_lineage()

    assert all(key.execution_requested is False for key in keys)
    assert all(key.side_effects_permitted is False for key in keys)
    assert all(
        record.execution_requested is False
        for record in rotations
    )
    assert all(
        record.side_effects_permitted is False
        for record in rotations
    )
    assert all(
        record.execution_requested is False
        for record in revocations
    )
    assert all(
        record.side_effects_permitted is False
        for record in revocations
    )