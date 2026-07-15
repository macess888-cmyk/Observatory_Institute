import pytest

from enums import (
    BindingStatus,
    ConfidenceLevel,
    ConflictStatus,
    ContinuityStatus,
    EventType,
    LineageStatus,
    OperationalStatus,
    RecoveryDecisionStatus,
    TransitionStatus,
)
from models import ContinuityClassification
from services.recovery_orchestrator import (
    RecoveryOrchestrationError,
    RecoveryOrchestrator,
)


def make_assessment(
    *,
    transition_id: str,
    event_type: EventType,
    transition_status: TransitionStatus,
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    missing_evidence: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
) -> ContinuityClassification:
    is_pass = operational_status is OperationalStatus.PASS

    return ContinuityClassification(
        transition_id=transition_id,
        event_type=event_type,
        service_continuity=(
            ContinuityStatus.CONTINUOUS
            if is_pass
            else ContinuityStatus.UNVERIFIED
        ),
        runtime_continuity=(
            ContinuityStatus.CONDITIONALLY_CONTINUOUS
            if is_pass
            else ContinuityStatus.UNVERIFIED
        ),
        execution_continuity=(
            ContinuityStatus.CONDITIONALLY_CONTINUOUS
            if is_pass
            else ContinuityStatus.UNVERIFIED
        ),
        state_continuity=(
            ContinuityStatus.CONDITIONALLY_CONTINUOUS
            if is_pass
            else ContinuityStatus.UNVERIFIED
        ),
        authority_continuity=(
            ContinuityStatus.CONTINUOUS
            if is_pass
            else ContinuityStatus.UNVERIFIED
        ),
        availability_continuity=(
            ContinuityStatus.CONTINUOUS
            if is_pass
            else ContinuityStatus.CONDITIONALLY_CONTINUOUS
        ),
        state_lineage=(
            LineageStatus.RECONCILED
            if is_pass
            else LineageStatus.UNVERIFIED
        ),
        binding_status=(
            BindingStatus.BOUND
            if is_pass
            else BindingStatus.UNVERIFIED
        ),
        conflict_status=(
            ConflictStatus.CLEAR
            if is_pass
            else ConflictStatus.UNKNOWN
        ),
        transition_status=transition_status,
        operational_status=operational_status,
        confidence=confidence,
        applied_rules=("TEST-RULE",),
        reasons=("Test assessment.",),
        missing_evidence=missing_evidence,
        conflicts=conflicts,
    )


def make_ready_assessments() -> tuple[ContinuityClassification, ...]:
    return (
        make_assessment(
            transition_id="AUTHORITY-CONVERGENCE:001",
            event_type=EventType.AUTHORITY_CONVERGENCE,
            transition_status=TransitionStatus.AUTHORITY_CONVERGED,
        ),
        make_assessment(
            transition_id="LINEAGE-RECONCILIATION:001",
            event_type=EventType.LINEAGE_RECONCILIATION,
            transition_status=TransitionStatus.LINEAGE_RECONCILED,
        ),
        make_assessment(
            transition_id="ROLLBACK-RECOVERY:001",
            event_type=EventType.ROLLBACK_RECOVERY,
            transition_status=TransitionStatus.ROLLBACK_RECOVERED,
        ),
    )


def test_orchestrator_returns_recovery_ready() -> None:
    assessments = make_ready_assessments()

    result = RecoveryOrchestrator().orchestrate(assessments)

    assert result.status is RecoveryDecisionStatus.RECOVERY_READY
    assert result.operational_status is OperationalStatus.PASS
    assert result.confidence is ConfidenceLevel.HIGH
    assert result.required_assessments == 3
    assert result.passed_assessments == 3
    assert result.held_assessments == 0
    assert result.missing_assessment_types == ()
    assert result.missing_evidence == ()
    assert result.conflicts == ()
    assert "RO-001" in result.applied_rules


def test_orchestrator_explains_recovery_ready() -> None:
    result = RecoveryOrchestrator().orchestrate(
        make_ready_assessments()
    )

    assert any(
        "authority" in reason.lower()
        for reason in result.reasons
    )
    assert any(
        "lineage" in reason.lower()
        for reason in result.reasons
    )
    assert any(
        "integrity" in reason.lower()
        or "rollback" in reason.lower()
        for reason in result.reasons
    )
    assert any(
        "observer-only" in reason.lower()
        for reason in result.reasons
    )


def test_orchestrator_returns_hold_when_assessment_is_held() -> None:
    authority, lineage, rollback = make_ready_assessments()

    held_lineage = make_assessment(
        transition_id=lineage.transition_id,
        event_type=lineage.event_type,
        transition_status=lineage.transition_status,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        missing_evidence=("conflict resolution evidence",),
    )

    result = RecoveryOrchestrator().orchestrate(
        (authority, held_lineage, rollback)
    )

    assert result.status is RecoveryDecisionStatus.RECOVERY_HOLD
    assert result.operational_status is OperationalStatus.HOLD
    assert result.confidence is ConfidenceLevel.LOW
    assert result.passed_assessments == 2
    assert result.held_assessments == 1
    assert "conflict resolution evidence" in result.missing_evidence
    assert "RO-002" in result.applied_rules


def test_orchestrator_returns_hold_when_conflict_exists() -> None:
    authority, lineage, rollback = make_ready_assessments()

    conflicted_authority = make_assessment(
        transition_id=authority.transition_id,
        event_type=authority.event_type,
        transition_status=authority.transition_status,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.MODERATE,
        conflicts=("Multiple PRIMARY holders remain.",),
    )

    result = RecoveryOrchestrator().orchestrate(
        (conflicted_authority, lineage, rollback)
    )

    assert result.status is RecoveryDecisionStatus.RECOVERY_HOLD
    assert result.operational_status is OperationalStatus.HOLD
    assert result.conflicts == ("Multiple PRIMARY holders remain.",)
    assert result.held_assessments == 1
    assert "RO-002" in result.applied_rules


def test_orchestrator_returns_hold_when_required_assessment_missing() -> None:
    authority, lineage, _ = make_ready_assessments()

    result = RecoveryOrchestrator().orchestrate(
        (authority, lineage)
    )

    assert result.status is RecoveryDecisionStatus.RECOVERY_HOLD
    assert result.operational_status is OperationalStatus.HOLD
    assert result.required_assessments == 3
    assert result.passed_assessments == 2
    assert result.missing_assessment_types == (
        EventType.ROLLBACK_RECOVERY,
    )
    assert "RO-003" in result.applied_rules


def test_orchestrator_rejects_duplicate_assessment_type() -> None:
    authority, lineage, rollback = make_ready_assessments()

    duplicate_authority = make_assessment(
        transition_id="AUTHORITY-CONVERGENCE:002",
        event_type=EventType.AUTHORITY_CONVERGENCE,
        transition_status=TransitionStatus.AUTHORITY_CONVERGED,
    )

    with pytest.raises(
        RecoveryOrchestrationError,
        match="duplicate",
    ):
        RecoveryOrchestrator().orchestrate(
            (
                authority,
                duplicate_authority,
                lineage,
                rollback,
            )
        )


def test_orchestrator_rejects_unexpected_assessment_type() -> None:
    authority, lineage, rollback = make_ready_assessments()

    unexpected = make_assessment(
        transition_id="PAUSE:001",
        event_type=EventType.PAUSE,
        transition_status=TransitionStatus.PAUSED,
    )

    with pytest.raises(
        RecoveryOrchestrationError,
        match="unexpected",
    ):
        RecoveryOrchestrator().orchestrate(
            (authority, lineage, rollback, unexpected)
        )


def test_orchestrator_rejects_non_tuple_input() -> None:
    assessments = make_ready_assessments()

    with pytest.raises(TypeError, match="tuple"):
        RecoveryOrchestrator().orchestrate(
            list(assessments)  # type: ignore[arg-type]
        )


def test_orchestrator_rejects_non_classification_member() -> None:
    authority, lineage, _ = make_ready_assessments()

    with pytest.raises(TypeError, match="ContinuityClassification"):
        RecoveryOrchestrator().orchestrate(
            (
                authority,
                lineage,
                "ROLLBACK-RECOVERY",
            )  # type: ignore[arg-type]
        )


def test_orchestrator_rejects_empty_assessment_set() -> None:
    with pytest.raises(
        RecoveryOrchestrationError,
        match="at least one",
    ):
        RecoveryOrchestrator().orchestrate(())


def test_orchestrator_does_not_mutate_assessments() -> None:
    assessments = make_ready_assessments()
    original = tuple(assessments)

    RecoveryOrchestrator().orchestrate(assessments)

    assert assessments == original


def test_orchestrator_preserves_observer_only_boundary() -> None:
    result = RecoveryOrchestrator().orchestrate(
        make_ready_assessments()
    )

    assert result.execution_requested is False
    assert result.side_effects_permitted is False