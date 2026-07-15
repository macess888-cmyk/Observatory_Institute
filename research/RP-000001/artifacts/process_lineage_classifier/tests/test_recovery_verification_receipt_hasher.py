from datetime import datetime, timezone

import pytest

from models import RecoveryVerificationReceipt
from services.recovery_verification_receipt_hasher import (
    RecoveryVerificationReceiptHasher,
    RecoveryVerificationReceiptHashingError,
)


ISSUED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

MANIFEST_DIGEST = "sha256:" + ("1" * 64)
AUDIT_ROOT_DIGEST = "sha256:" + ("2" * 64)
DECISION_DIGEST = "sha256:" + ("3" * 64)


def make_receipt(
    *,
    receipt_id: str = "RVR-001",
    verification_id: str = "RDV-001",
    replay_id: str = "RDR-001",
    original_decision_id: str = "RD-001",
    replay_manifest_id: str = "RIM-001",
    replay_manifest_digest: str = MANIFEST_DIGEST,
    audit_chain_id: str = "AHC-001",
    audit_root_digest: str = AUDIT_ROOT_DIGEST,
    decision_digest: str = DECISION_DIGEST,
    verified: bool = True,
    issued_at: datetime = ISSUED_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> RecoveryVerificationReceipt:
    return RecoveryVerificationReceipt(
        receipt_id=receipt_id,
        verification_id=verification_id,
        replay_id=replay_id,
        original_decision_id=original_decision_id,
        replay_manifest_id=replay_manifest_id,
        replay_manifest_digest=replay_manifest_digest,
        audit_chain_id=audit_chain_id,
        audit_root_digest=audit_root_digest,
        decision_digest=decision_digest,
        verified=verified,
        issued_at=issued_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_returns_sha256_digest() -> None:
    result = RecoveryVerificationReceiptHasher().hash(make_receipt())

    assert result.algorithm == "sha256"
    assert result.digest.startswith("sha256:")
    assert len(result.digest.removeprefix("sha256:")) == 64
    assert result.receipt_id == "RVR-001"
    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_hasher_is_deterministic() -> None:
    receipt = make_receipt()

    first = RecoveryVerificationReceiptHasher().hash(receipt)
    second = RecoveryVerificationReceiptHasher().hash(receipt)

    assert first == second
    assert first.digest == second.digest
    assert first.canonical_payload == second.canonical_payload


def test_hasher_produces_same_digest_for_equivalent_receipts() -> None:
    first = make_receipt()
    second = make_receipt()

    assert (
        RecoveryVerificationReceiptHasher().hash(first).digest
        == RecoveryVerificationReceiptHasher().hash(second).digest
    )


def test_hasher_preserves_canonical_field_order() -> None:
    result = RecoveryVerificationReceiptHasher().hash(make_receipt())

    expected_keys = (
        "receipt_id",
        "verification_id",
        "replay_id",
        "original_decision_id",
        "replay_manifest_id",
        "replay_manifest_digest",
        "audit_chain_id",
        "audit_root_digest",
        "decision_digest",
        "verified",
        "issued_at",
        "issuer_id",
        "execution_requested",
        "side_effects_permitted",
    )

    positions = tuple(
        result.canonical_payload.index(f'"{key}"')
        for key in expected_keys
    )

    assert positions == tuple(sorted(positions))


def test_hasher_serializes_verified_boolean() -> None:
    result = RecoveryVerificationReceiptHasher().hash(make_receipt())

    assert '"verified":true' in result.canonical_payload


def test_hasher_serializes_timestamp_in_iso_format() -> None:
    result = RecoveryVerificationReceiptHasher().hash(make_receipt())

    assert ISSUED_AT.isoformat() in result.canonical_payload


@pytest.mark.parametrize(
    ("field_name", "first_value", "second_value"),
    [
        ("receipt_id", "RVR-001", "RVR-002"),
        ("verification_id", "RDV-001", "RDV-002"),
        ("replay_id", "RDR-001", "RDR-002"),
        ("original_decision_id", "RD-001", "RD-002"),
        ("replay_manifest_id", "RIM-001", "RIM-002"),
        (
            "replay_manifest_digest",
            MANIFEST_DIGEST,
            "sha256:" + ("4" * 64),
        ),
        ("audit_chain_id", "AHC-001", "AHC-002"),
        (
            "audit_root_digest",
            AUDIT_ROOT_DIGEST,
            "sha256:" + ("5" * 64),
        ),
        (
            "decision_digest",
            DECISION_DIGEST,
            "sha256:" + ("6" * 64),
        ),
        (
            "issuer_id",
            "PROCESS-LINEAGE-CLASSIFIER",
            "OTHER-ISSUER",
        ),
    ],
)
def test_hasher_is_sensitive_to_field_change(
    field_name: str,
    first_value: str,
    second_value: str,
) -> None:
    first = RecoveryVerificationReceiptHasher().hash(
        make_receipt(**{field_name: first_value})
    )
    second = RecoveryVerificationReceiptHasher().hash(
        make_receipt(**{field_name: second_value})
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_issue_time() -> None:
    first = RecoveryVerificationReceiptHasher().hash(make_receipt())
    second = RecoveryVerificationReceiptHasher().hash(
        make_receipt(
            issued_at=datetime(
                2026,
                7,
                15,
                12,
                0,
                1,
                tzinfo=timezone.utc,
            )
        )
    )

    assert first.digest != second.digest


def test_hasher_rejects_non_receipt_input() -> None:
    with pytest.raises(TypeError, match="RecoveryVerificationReceipt"):
        RecoveryVerificationReceiptHasher().hash(
            "RVR-001"  # type: ignore[arg-type]
        )


def test_hasher_does_not_mutate_receipt() -> None:
    receipt = make_receipt()
    original = receipt

    RecoveryVerificationReceiptHasher().hash(receipt)

    assert receipt == original


def test_hasher_preserves_observer_only_boundary() -> None:
    result = RecoveryVerificationReceiptHasher().hash(make_receipt())

    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_hash_result_is_immutable() -> None:
    result = RecoveryVerificationReceiptHasher().hash(make_receipt())

    with pytest.raises((AttributeError, TypeError)):
        result.digest = "sha256:changed"  # type: ignore[misc]


def test_hash_result_rejects_invalid_algorithm() -> None:
    from models import RecoveryVerificationReceiptHash

    with pytest.raises(
        RecoveryVerificationReceiptHashingError,
        match="algorithm",
    ):
        RecoveryVerificationReceiptHash(
            receipt_id="RVR-001",
            algorithm="md5",
            digest="md5:invalid",
            canonical_payload="{}",
            execution_requested=False,
            side_effects_permitted=False,
        )