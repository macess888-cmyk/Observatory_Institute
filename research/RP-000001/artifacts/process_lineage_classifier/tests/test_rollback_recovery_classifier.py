from datetime import datetime, timedelta, timezone

import pytest

from enums import (
    BindingStatus,
    ConfidenceLevel,
    ConflictStatus,
    ContinuityStatus,
    EventType,
    LineageStatus,
    OperationalStatus,
    TransitionStatus,
)
from models import ProcessEvent
from services.rollback_recovery_classifier import (
    RollbackRecoveryClassificationError,
    RollbackRecoveryClassifier,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    runtime_id: str,
    execution_id: str,
    state_id: str,
    host_id: str,
    address: str,
    authority_role: str,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    snapshot_id: str | None = None,
    service_id: str = "SERVICE-A",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=EventType.ROLLBACK_RECOVERY,
        timestamp=datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
        + timedelta(seconds=sequence_number),
        sequence_number=sequence_number,
        service_id=service_id,
        runtime_id=runtime_id,
        execution_id=execution_id,
        state_id=state_id,
        host_id=host_id,
        address=address,
        authority_role=authority_role,
        parent_event_ids=parent_event_ids,
        parent_state_ids=parent_state_ids,
        evidence_ids=evidence_ids,
        snapshot_id=snapshot_id,
    )


def make_valid_recovery() -> tuple[ProcessEvent, ProcessEvent]:
    rollback = make_event(
        event_id="EV-001",
        sequence_number=1,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        host_id="HOST-A",
        address="10.0.0.10",
        authority_role="PRIMARY",
        evidence_ids=(
            "EVD-ROLLBACK-VERIFIED-001",
            "EVD-RECOVERY-BASELINE-001",
        ),
        snapshot_id="SNAPSHOT-100",
    )
    recovered = make_event(
        event_id="EV-002",
        sequence_number=2,
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-200",
        host_id="HOST-A",
        address="10.0.0.10",
        authority_role="PRIMARY",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-100",),
        evidence_ids=(
            "EVD-ROLLBACK-RECOVERY-001",
            "EVD-FORWARD-STATE-VERIFY-001",
            "EVD-INTEGRITY-CHECK-001",
            "EVD-AUTHORITY-PRESERVE-001",
            "EVD-RECOVERY-COMPLETE-001",
        ),
        snapshot_id="SNAPSHOT-200",
    )
    return rollback, recovered


def test_classifier_accepts_verified_rollback_recovery() -> None:
    rollback, recovered = make_valid_recovery()
    result = RollbackRecoveryClassifier().classify(rollback, recovered)

    assert result.event_type is EventType.ROLLBACK_RECOVERY
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert result.runtime_continuity is ContinuityStatus.CONTINUOUS
    assert result.execution_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_continuity is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert result.availability_continuity is ContinuityStatus.CONTINUOUS
    assert result.state_lineage is LineageStatus.RECONCILED
    assert result.binding_status is BindingStatus.BOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.ROLLBACK_RECOVERED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "RKR-001" in result.applied_rules


def test_classifier_explains_verified_recovery() -> None:
    rollback, recovered = make_valid_recovery()
    result = RollbackRecoveryClassifier().classify(rollback, recovered)

    assert any("rollback" in reason.lower() for reason in result.reasons)
    assert any("forward state" in reason.lower() for reason in result.reasons)
    assert any("integrity" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_returns_hold_for_incomplete_recovery_evidence() -> None:
    rollback, recovered = make_valid_recovery()
    unverified = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_event_ids=recovered.parent_event_ids,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=(),
        snapshot_id=recovered.snapshot_id,
    )

    result = RollbackRecoveryClassifier().classify(rollback, unverified)

    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_lineage is LineageStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.conflict_status is ConflictStatus.UNKNOWN
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence
    assert "RKR-002" in result.applied_rules


def test_classifier_returns_hold_for_integrity_conflict() -> None:
    rollback, recovered = make_valid_recovery()
    conflicted = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_event_ids=recovered.parent_event_ids,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=(
            "EVD-ROLLBACK-RECOVERY-001",
            "EVD-FORWARD-STATE-VERIFY-001",
            "EVD-INTEGRITY-CONFLICT-001",
            "EVD-AUTHORITY-PRESERVE-001",
            "EVD-RECOVERY-COMPLETE-001",
        ),
        snapshot_id=recovered.snapshot_id,
    )

    result = RollbackRecoveryClassifier().classify(rollback, conflicted)

    assert result.state_continuity is ContinuityStatus.CONFLICTED
    assert result.state_lineage is LineageStatus.CONFLICTED
    assert result.binding_status is BindingStatus.COLLIDING
    assert result.conflict_status is ConflictStatus.CONFLICTED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts
    assert "RKR-003" in result.applied_rules


def test_classifier_returns_hold_for_stale_recovery_state() -> None:
    rollback, recovered = make_valid_recovery()
    stale = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id="STATE-050",
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_event_ids=recovered.parent_event_ids,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=(
            "EVD-ROLLBACK-RECOVERY-001",
            "EVD-STALE-RECOVERY-STATE-001",
            "EVD-INTEGRITY-CHECK-001",
            "EVD-AUTHORITY-PRESERVE-001",
            "EVD-RECOVERY-COMPLETE-001",
        ),
        snapshot_id="SNAPSHOT-050",
    )

    result = RollbackRecoveryClassifier().classify(rollback, stale)

    assert result.state_continuity is ContinuityStatus.DEGRADED
    assert result.state_lineage is LineageStatus.DISCONTINUOUS
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.MODERATE
    assert result.conflicts
    assert "RKR-004" in result.applied_rules


def test_classifier_rejects_wrong_current_event_type() -> None:
    rollback, recovered = make_valid_recovery()
    invalid = ProcessEvent(
        event_id=recovered.event_id,
        event_type=EventType.ROLLBACK,
        timestamp=recovered.timestamp,
        sequence_number=recovered.sequence_number,
        service_id=recovered.service_id,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_event_ids=recovered.parent_event_ids,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=recovered.evidence_ids,
        snapshot_id=recovered.snapshot_id,
    )

    with pytest.raises(
        RollbackRecoveryClassificationError,
        match="ROLLBACK_RECOVERY",
    ):
        RollbackRecoveryClassifier().classify(rollback, invalid)


@pytest.mark.parametrize(
    ("field", "replacement", "pattern"),
    [
        ("runtime_id", "RUNTIME-B", "runtime"),
        ("execution_id", "EXEC-B", "execution"),
        ("service_id", "SERVICE-B", "service"),
        ("authority_role", "SECONDARY", "authority"),
    ],
)
def test_classifier_rejects_changed_identity_or_role(
    field: str,
    replacement: str,
    pattern: str,
) -> None:
    rollback, recovered = make_valid_recovery()
    values = {
        "runtime_id": recovered.runtime_id,
        "execution_id": recovered.execution_id,
        "service_id": recovered.service_id,
        "authority_role": recovered.authority_role,
    }
    values[field] = replacement

    invalid = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=values["runtime_id"],
        execution_id=values["execution_id"],
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=values["authority_role"],
        parent_event_ids=recovered.parent_event_ids,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=recovered.evidence_ids,
        snapshot_id=recovered.snapshot_id,
        service_id=values["service_id"],
    )

    with pytest.raises(
        RollbackRecoveryClassificationError,
        match=f"(?i){pattern}",
    ):
        RollbackRecoveryClassifier().classify(rollback, invalid)


def test_classifier_rejects_missing_parent_link() -> None:
    rollback, recovered = make_valid_recovery()
    invalid = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=recovered.evidence_ids,
        snapshot_id=recovered.snapshot_id,
    )

    with pytest.raises(RollbackRecoveryClassificationError, match="(?i)parent"):
        RollbackRecoveryClassifier().classify(rollback, invalid)


def test_classifier_rejects_missing_parent_state() -> None:
    rollback, recovered = make_valid_recovery()
    invalid = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_event_ids=recovered.parent_event_ids,
        evidence_ids=recovered.evidence_ids,
        snapshot_id=recovered.snapshot_id,
    )

    with pytest.raises(RollbackRecoveryClassificationError, match="(?i)state"):
        RollbackRecoveryClassifier().classify(rollback, invalid)


def test_classifier_rejects_missing_snapshot() -> None:
    rollback, recovered = make_valid_recovery()
    invalid = make_event(
        event_id=recovered.event_id,
        sequence_number=recovered.sequence_number,
        runtime_id=recovered.runtime_id,
        execution_id=recovered.execution_id,
        state_id=recovered.state_id,
        host_id=recovered.host_id,
        address=recovered.address,
        authority_role=recovered.authority_role,
        parent_event_ids=recovered.parent_event_ids,
        parent_state_ids=recovered.parent_state_ids,
        evidence_ids=recovered.evidence_ids,
    )

    with pytest.raises(RollbackRecoveryClassificationError, match="(?i)snapshot"):
        RollbackRecoveryClassifier().classify(rollback, invalid)


def test_classifier_requires_process_event_inputs() -> None:
    _, recovered = make_valid_recovery()

    with pytest.raises(TypeError, match="ProcessEvent"):
        RollbackRecoveryClassifier().classify(
            "EV-001",  # type: ignore[arg-type]
            recovered,
        )