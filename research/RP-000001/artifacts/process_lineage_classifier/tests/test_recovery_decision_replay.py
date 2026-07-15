from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import (
    RecoveryDecision,
    RecoveryDecisionReplay,
)
from services.recovery_decision_replay_service import (
    RecoveryDecisionReplayError,
    RecoveryDecisionReplayService,
)


REPLAYED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_decision(
    *,
    status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    operational_status: OperationalStatus = OperationalStatus.PASS,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    passed_assessments: int = 3,
    held_assessments: int = 0,
    missing_assessment_types: tuple[EventType, ...] = (),
    applied_rules: tuple[str, ...] = ("RO-001",),
    reasons: tuple[str, ...] = (
        "Recovery readiness was established.",
    ),
    missing_evidence: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
) -> RecoveryDecision:
    return RecoveryDecision(
        status=status,
        operational_status=operational_status,
        confidence=confidence,
        required_assessments=3,
        passed_assessments=passed_assessments,
        held_assessments=held_assessments,
        missing_assessment_types=missing_assessment_types,
        applied_rules=applied_rules,
        reasons=reasons,
        missing_evidence=missing_evidence,
        conflicts=conflicts,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_replays_ready_decision() -> None:
    decision = make_decision()

    replay = RecoveryDecisionReplayService().replay(
        replay_id="RDR-001",
        original_decision_id="RD-001",
        decision=decision,
        assessment_ids=(
            "AUTHORITY-CONVERGENCE:001",
            "LINEAGE-RECONCILIATION:001",
            "ROLLBACK-RECOVERY:001",
        ),
        evidence_ids=(
            "EVD-QUORUM-001",
            "EVD-LINEAGE-001",
            "EVD-INTEGRITY-001",
        ),
        replayed_at=REPLAYED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert isinstance(replay, RecoveryDecisionReplay)
    assert replay.replay_id == "RDR-001"
    assert replay.original_decision_id == "RD-001"
    assert replay.original_status is RecoveryDecisionStatus.RECOVERY_READY
    assert replay.replayed_status is RecoveryDecisionStatus.RECOVERY_READY
    assert replay.original_operational_status is OperationalStatus.PASS
    assert replay.replayed_operational_status is OperationalStatus.PASS
    assert replay.original_confidence is ConfidenceLevel.HIGH
    assert replay.replayed_confidence is ConfidenceLevel.HIGH
    assert replay.status_match is True
    assert replay.operational_status_match is True
    assert replay.confidence_match is True
    assert replay.rules_match is True
    assert replay.reasons_match is True
    assert replay.missing_evidence_match is True
    assert replay.conflicts_match is True
    assert replay.replay_verified is True
    assert replay.execution_requested is False
    assert replay.side_effects_permitted is False


def test_service_replays_held_decision() -> None:
    decision = make_decision(
        status=RecoveryDecisionStatus.RECOVERY_HOLD,
        operational_status=OperationalStatus.HOLD,
        confidence=ConfidenceLevel.LOW,
        passed_assessments=2,
        held_assessments=1,
        missing_assessment_types=(
            EventType.ROLLBACK_RECOVERY,
        ),
        applied_rules=("RO-003",),
        reasons=("Required recovery assessment is missing.",),
        missing_evidence=("ROLLBACK_RECOVERY assessment",),
    )

    replay = RecoveryDecisionReplayService().replay(
        replay_id="RDR-002",
        original_decision_id="RD-002",
        decision=decision,
        assessment_ids=(
            "AUTHORITY-CONVERGENCE:001",
            "LINEAGE-RECONCILIATION:001",
        ),
        evidence_ids=(
            "EVD-QUORUM-001",
            "EVD-LINEAGE-001",
        ),
        replayed_at=REPLAYED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert replay.original_status is RecoveryDecisionStatus.RECOVERY_HOLD
    assert replay.replayed_status is RecoveryDecisionStatus.RECOVERY_HOLD
    assert replay.replay_verified is True
    assert replay.missing_evidence_match is True


def test_service_preserves_assessment_references() -> None:
    assessment_ids = (
        "AUTHORITY-CONVERGENCE:001",
        "LINEAGE-RECONCILIATION:001",
        "ROLLBACK-RECOVERY:001",
    )

    replay = RecoveryDecisionReplayService().replay(
        replay_id="RDR-001",
        original_decision_id="RD-001",
        decision=make_decision(),
        assessment_ids=assessment_ids,
        evidence_ids=("EVD-001",),
        replayed_at=REPLAYED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert replay.assessment_ids == assessment_ids


def test_service_preserves_evidence_references() -> None:
    evidence_ids = (
        "EVD-QUORUM-001",
        "EVD-LINEAGE-001",
        "EVD-INTEGRITY-001",
    )

    replay = RecoveryDecisionReplayService().replay(
        replay_id="RDR-001",
        original_decision_id="RD-001",
        decision=make_decision(),
        assessment_ids=("ASSESSMENT-001",),
        evidence_ids=evidence_ids,
        replayed_at=REPLAYED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert replay.evidence_ids == evidence_ids


def test_service_rejects_non_decision_input() -> None:
    with pytest.raises(TypeError, match="RecoveryDecision"):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision="RECOVERY_READY",  # type: ignore[arg-type]
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=("EVD-001",),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_replay_id() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="replay_id",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=("EVD-001",),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_original_decision_id() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="original_decision_id",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="",
            decision=make_decision(),
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=("EVD-001",),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_assessment_references() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="assessment",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=(),
            evidence_ids=("EVD-001",),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_evidence_references() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="evidence",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=(),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_assessment_references() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="duplicate assessment",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=(
                "ASSESSMENT-001",
                "ASSESSMENT-001",
            ),
            evidence_ids=("EVD-001",),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_duplicate_evidence_references() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="duplicate evidence",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=(
                "EVD-001",
                "EVD-001",
            ),
            replayed_at=REPLAYED_AT,
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_naive_replay_time() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="timezone-aware",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=("EVD-001",),
            replayed_at=datetime(2026, 7, 14, 12, 0),
            replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_service_rejects_empty_replayer_id() -> None:
    with pytest.raises(
        RecoveryDecisionReplayError,
        match="replayer_id",
    ):
        RecoveryDecisionReplayService().replay(
            replay_id="RDR-001",
            original_decision_id="RD-001",
            decision=make_decision(),
            assessment_ids=("ASSESSMENT-001",),
            evidence_ids=("EVD-001",),
            replayed_at=REPLAYED_AT,
            replayer_id="",
        )


def test_service_does_not_mutate_decision() -> None:
    decision = make_decision()
    original = decision

    RecoveryDecisionReplayService().replay(
        replay_id="RDR-001",
        original_decision_id="RD-001",
        decision=decision,
        assessment_ids=("ASSESSMENT-001",),
        evidence_ids=("EVD-001",),
        replayed_at=REPLAYED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert decision == original


def test_service_preserves_observer_only_boundary() -> None:
    replay = RecoveryDecisionReplayService().replay(
        replay_id="RDR-001",
        original_decision_id="RD-001",
        decision=make_decision(),
        assessment_ids=("ASSESSMENT-001",),
        evidence_ids=("EVD-001",),
        replayed_at=REPLAYED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert replay.execution_requested is False
    assert replay.side_effects_permitted is False