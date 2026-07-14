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
from services.migration_classifier import (
    MigrationClassificationError,
    MigrationClassifier,
)


def make_event(
    *,
    event_id: str,
    sequence_number: int,
    event_type: EventType,
    host_id: str,
    address: str,
    parent_event_ids: tuple[str, ...] = (),
    parent_state_ids: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
    migration_id: str | None = None,
    service_id: str = "SERVICE-A",
    runtime_id: str = "RUNTIME-001",
    execution_id: str = "EXEC-001",
    state_id: str = "STATE-001",
    authority_role: str = "PRIMARY",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=event_type,
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
        migration_id=migration_id,
    )


def test_classifier_accepts_valid_migration() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=(
            "EVD-MIGRATION-001",
            "EVD-STATE-TRANSFER-001",
            "EVD-SOURCE-DEACTIVATION-001",
        ),
        migration_id="MIGRATION-001",
    )

    result = MigrationClassifier().classify(previous, current)

    assert result.event_type is EventType.MIGRATE
    assert result.service_continuity is ContinuityStatus.CONTINUOUS
    assert (
        result.runtime_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert (
        result.execution_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert result.state_continuity is ContinuityStatus.CONTINUOUS
    assert result.authority_continuity is ContinuityStatus.CONTINUOUS
    assert (
        result.availability_continuity
        is ContinuityStatus.CONDITIONALLY_CONTINUOUS
    )
    assert result.state_lineage is LineageStatus.LINEAR
    assert result.binding_status is BindingStatus.REBOUND
    assert result.conflict_status is ConflictStatus.CLEAR
    assert result.transition_status is TransitionStatus.MIGRATED
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert "MG-001" in result.applied_rules


def test_classifier_returns_hold_for_unverified_migration() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        migration_id="MIGRATION-001",
    )

    result = MigrationClassifier().classify(previous, current)

    assert result.runtime_continuity is ContinuityStatus.UNVERIFIED
    assert result.execution_continuity is ContinuityStatus.UNKNOWN
    assert result.state_continuity is ContinuityStatus.UNVERIFIED
    assert result.state_lineage is LineageStatus.UNVERIFIED
    assert result.binding_status is BindingStatus.UNVERIFIED
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.missing_evidence


def test_classifier_explains_valid_migration() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        parent_state_ids=("STATE-001",),
        evidence_ids=(
            "EVD-MIGRATION-001",
            "EVD-STATE-TRANSFER-001",
            "EVD-SOURCE-DEACTIVATION-001",
        ),
        migration_id="MIGRATION-001",
    )

    result = MigrationClassifier().classify(previous, current)

    assert any("host" in reason.lower() for reason in result.reasons)
    assert any("migration" in reason.lower() for reason in result.reasons)
    assert result.missing_evidence == ()
    assert result.conflicts == ()


def test_classifier_rejects_wrong_current_event_type() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.RESTART,
        host_id="HOST-002",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
    )

    with pytest.raises(MigrationClassificationError, match="MIGRATE"):
        MigrationClassifier().classify(previous, current)


def test_classifier_rejects_unchanged_host() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-001",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        migration_id="MIGRATION-001",
    )

    with pytest.raises(MigrationClassificationError, match="(?i)host"):
        MigrationClassifier().classify(previous, current)


def test_classifier_rejects_changed_service_identity() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
        service_id="SERVICE-A",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        service_id="SERVICE-B",
        parent_event_ids=("EV-001",),
        migration_id="MIGRATION-001",
    )

    with pytest.raises(MigrationClassificationError, match="(?i)service"):
        MigrationClassifier().classify(previous, current)


def test_classifier_rejects_changed_runtime_identity() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
        runtime_id="RUNTIME-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        runtime_id="RUNTIME-002",
        parent_event_ids=("EV-001",),
        migration_id="MIGRATION-001",
    )

    with pytest.raises(MigrationClassificationError, match="(?i)runtime"):
        MigrationClassifier().classify(previous, current)


def test_classifier_rejects_changed_execution_identity() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
        execution_id="EXEC-001",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        execution_id="EXEC-002",
        parent_event_ids=("EV-001",),
        migration_id="MIGRATION-001",
    )

    with pytest.raises(MigrationClassificationError, match="(?i)execution"):
        MigrationClassifier().classify(previous, current)


def test_classifier_rejects_missing_parent_link() -> None:
    previous = make_event(
        event_id="EV-001",
        sequence_number=1,
        event_type=EventType.START,
        host_id="HOST-001",
        address="10.0.0.10",
    )
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        migration_id="MIGRATION-001",
    )

    with pytest.raises(MigrationClassificationError, match="(?i)parent"):
        MigrationClassifier().classify(previous, current)


def test_classifier_requires_process_event_inputs() -> None:
    current = make_event(
        event_id="EV-002",
        sequence_number=2,
        event_type=EventType.MIGRATE,
        host_id="HOST-002",
        address="10.0.0.20",
        parent_event_ids=("EV-001",),
        migration_id="MIGRATION-001",
    )

    with pytest.raises(TypeError, match="ProcessEvent"):
        MigrationClassifier().classify(
            "EV-001", current  # type: ignore[arg-type]
        )