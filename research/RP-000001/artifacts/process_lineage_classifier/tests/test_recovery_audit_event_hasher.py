from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import RecoveryAuditEvent
from services.recovery_audit_event_hasher import (
    RecoveryAuditEventHasher,
    RecoveryAuditEventHashingError,
)


OCCURRED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str = "AUD-001",
    sequence_number: int = 1,
    event_type: str = "RECONCILIATION_RECEIPT_ISSUED",
    recovery_status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    occurred_at: datetime = OCCURRED_AT,
    actor_id: str = "PROCESS-LINEAGE-CLASSIFIER",
    related_receipt_id: str | None = "RCP-001",
    evidence_ids: tuple[str, ...] = (
        "EVD-QUORUM-001",
        "EVD-LINEAGE-001",
    ),
    reasons: tuple[str, ...] = (
        "Reconciliation receipt issued.",
    ),
    conflicts: tuple[str, ...] = (),
) -> RecoveryAuditEvent:
    return RecoveryAuditEvent(
        event_id=event_id,
        sequence_number=sequence_number,
        event_type=event_type,
        recovery_status=recovery_status,
        operational_status=operational_status,
        confidence=confidence,
        occurred_at=occurred_at,
        actor_id=actor_id,
        related_receipt_id=related_receipt_id,
        evidence_ids=evidence_ids,
        reasons=reasons,
        conflicts=conflicts,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_returns_sha256_digest() -> None:
    result = RecoveryAuditEventHasher().hash(make_event())

    assert result.algorithm == "sha256"
    assert result.digest.startswith("sha256:")
    assert len(result.digest.removeprefix("sha256:")) == 64
    assert result.event_id == "AUD-001"
    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_hasher_is_deterministic() -> None:
    event = make_event()

    first = RecoveryAuditEventHasher().hash(event)
    second = RecoveryAuditEventHasher().hash(event)

    assert first == second
    assert first.digest == second.digest
    assert first.canonical_payload == second.canonical_payload


def test_hasher_produces_same_digest_for_equivalent_events() -> None:
    first = make_event()
    second = make_event()

    assert (
        RecoveryAuditEventHasher().hash(first).digest
        == RecoveryAuditEventHasher().hash(second).digest
    )


def test_hasher_preserves_canonical_field_order() -> None:
    result = RecoveryAuditEventHasher().hash(make_event())

    expected_keys = (
        "event_id",
        "sequence_number",
        "event_type",
        "recovery_status",
        "operational_status",
        "confidence",
        "occurred_at",
        "actor_id",
        "related_receipt_id",
        "evidence_ids",
        "reasons",
        "conflicts",
        "execution_requested",
        "side_effects_permitted",
    )

    positions = tuple(
        result.canonical_payload.index(f'"{key}"')
        for key in expected_keys
    )

    assert positions == tuple(sorted(positions))


def test_hasher_serializes_enum_values() -> None:
    result = RecoveryAuditEventHasher().hash(make_event())

    assert '"recovery_status":"RECOVERY_READY"' in result.canonical_payload
    assert '"operational_status":"PASS"' in result.canonical_payload
    assert '"confidence":"HIGH"' in result.canonical_payload


def test_hasher_serializes_timestamp_in_iso_format() -> None:
    result = RecoveryAuditEventHasher().hash(make_event())

    assert OCCURRED_AT.isoformat() in result.canonical_payload


def test_hasher_serializes_null_receipt_identity() -> None:
    result = RecoveryAuditEventHasher().hash(
        make_event(
            event_type="RECOVERY_ASSESSMENT_STARTED",
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            related_receipt_id=None,
        )
    )

    assert '"related_receipt_id":null' in result.canonical_payload


def test_hasher_is_sensitive_to_event_identity() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(event_id="AUD-001")
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(event_id="AUD-002")
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_sequence_number() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(sequence_number=1)
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(sequence_number=2)
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_event_type() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(event_type="RECONCILIATION_RECEIPT_ISSUED")
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(event_type="RECOVERY_ASSESSMENT_COMPLETED")
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_status() -> None:
    ready = RecoveryAuditEventHasher().hash(make_event())
    held = RecoveryAuditEventHasher().hash(
        make_event(
            recovery_status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
        )
    )

    assert ready.digest != held.digest


def test_hasher_is_sensitive_to_actor_identity() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(actor_id="PROCESS-LINEAGE-CLASSIFIER")
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(actor_id="OTHER-ACTOR")
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_receipt_identity() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(related_receipt_id="RCP-001")
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(related_receipt_id="RCP-002")
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_evidence_references() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(
            evidence_ids=(
                "EVD-QUORUM-001",
                "EVD-LINEAGE-001",
            )
        )
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(
            evidence_ids=(
                "EVD-QUORUM-999",
                "EVD-LINEAGE-001",
            )
        )
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_reasons() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(reasons=("Original reason.",))
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(reasons=("Changed reason.",))
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_conflicts() -> None:
    first = RecoveryAuditEventHasher().hash(
        make_event(conflicts=())
    )
    second = RecoveryAuditEventHasher().hash(
        make_event(conflicts=("Authority conflict.",))
    )

    assert first.digest != second.digest


def test_hasher_is_sensitive_to_timestamp() -> None:
    first = RecoveryAuditEventHasher().hash(make_event())
    second = RecoveryAuditEventHasher().hash(
        make_event(
            occurred_at=datetime(
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


def test_hasher_rejects_non_event_input() -> None:
    with pytest.raises(TypeError, match="RecoveryAuditEvent"):
        RecoveryAuditEventHasher().hash(
            "AUD-001"  # type: ignore[arg-type]
        )


def test_hasher_does_not_mutate_event() -> None:
    event = make_event()
    original = event

    RecoveryAuditEventHasher().hash(event)

    assert event == original


def test_hasher_preserves_observer_only_boundary() -> None:
    result = RecoveryAuditEventHasher().hash(make_event())

    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_hash_result_is_immutable() -> None:
    result = RecoveryAuditEventHasher().hash(make_event())

    with pytest.raises((AttributeError, TypeError)):
        result.digest = "sha256:changed"  # type: ignore[misc]


def test_hash_result_rejects_invalid_algorithm() -> None:
    from models import RecoveryAuditEventHash

    with pytest.raises(
        RecoveryAuditEventHashingError,
        match="algorithm",
    ):
        RecoveryAuditEventHash(
            event_id="AUD-001",
            algorithm="md5",
            digest="md5:invalid",
            canonical_payload="{}",
            execution_requested=False,
            side_effects_permitted=False,
        )