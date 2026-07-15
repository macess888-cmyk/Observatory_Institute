from datetime import datetime, timezone

import pytest

from enums import (
    ConfidenceLevel,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import (
    RecoveryDecisionReplay,
    RecoveryDecisionVerification,
)
from services.recovery_decision_verifier import (
    RecoveryDecisionVerificationError,
    RecoveryDecisionVerifier,
)


VERIFIED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_replay(
    *,
    replay_id: str = "RDR-001",
    original_decision_id: str = "RD-001",
    original_status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    replayed_status: RecoveryDecisionStatus = (
        RecoveryDecisionStatus.RECOVERY_READY
    ),
    original_operational_status: OperationalStatus = (
        OperationalStatus.PASS
    ),
    replayed_operational_status: OperationalStatus = (
        OperationalStatus.PASS
    ),
    original_confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    replayed_confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    status_match: bool = True,
    operational_status_match: bool = True,
    confidence_match: bool = True,
    rules_match: bool = True,
    reasons_match: bool = True,
    missing_evidence_match: bool = True,
    conflicts_match: bool = True,
    replay_verified: bool = True,
) -> RecoveryDecisionReplay:
    return RecoveryDecisionReplay(
        replay_id=replay_id,
        original_decision_id=original_decision_id,
        original_status=original_status,
        replayed_status=replayed_status,
        original_operational_status=original_operational_status,
        replayed_operational_status=replayed_operational_status,
        original_confidence=original_confidence,
        replayed_confidence=replayed_confidence,
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
        original_rules=("RO-001",),
        replayed_rules=("RO-001",),
        original_reasons=("Recovery readiness was established.",),
        replayed_reasons=("Recovery readiness was established.",),
        original_missing_evidence=(),
        replayed_missing_evidence=(),
        original_conflicts=(),
        replayed_conflicts=(),
        status_match=status_match,
        operational_status_match=operational_status_match,
        confidence_match=confidence_match,
        rules_match=rules_match,
        reasons_match=reasons_match,
        missing_evidence_match=missing_evidence_match,
        conflicts_match=conflicts_match,
        replay_verified=replay_verified,
        replayed_at=VERIFIED_AT,
        replayer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_verifier_accepts_verified_replay() -> None:
    result = RecoveryDecisionVerifier().verify(
        verification_id="RDV-001",
        replay=make_replay(),
        verified_at=VERIFIED_AT,
        verifier_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert isinstance(result, RecoveryDecisionVerification)
    assert result.verification_id == "RDV-001"
    assert result.replay_id == "RDR-001"
    assert result.original_decision_id == "RD-001"
    assert result.verified is True
    assert result.replay_verified is True
    assert result.status_match is True
    assert result.operational_status_match is True
    assert result.confidence_match is True
    assert result.rules_match is True
    assert result.reasons_match is True
    assert result.missing_evidence_match is True
    assert result.conflicts_match is True
    assert result.execution_requested is False
    assert result.side_effects_permitted is False


def test_verifier_accepts_verified_hold_replay() -> None:
    replay = make_replay(
        original_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        replayed_status=RecoveryDecisionStatus.RECOVERY_HOLD,
        original_operational_status=OperationalStatus.HOLD,
        replayed_operational_status=OperationalStatus.HOLD,
        original_confidence=ConfidenceLevel.LOW,
        replayed_confidence=ConfidenceLevel.LOW,
    )

    result = RecoveryDecisionVerifier().verify(
        verification_id="RDV-002",
        replay=replay,
        verified_at=VERIFIED_AT,
        verifier_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert result.verified is True
    assert result.replay_verified is True


def test_verifier_rejects_unverified_replay() -> None:
    replay = make_replay(
        status_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="status mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_status_mismatch() -> None:
    replay = make_replay(
        status_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="status mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_operational_status_mismatch() -> None:
    replay = make_replay(
        operational_status_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="operational status mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_confidence_mismatch() -> None:
    replay = make_replay(
        confidence_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="confidence mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_rules_mismatch() -> None:
    replay = make_replay(
        rules_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="rules mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_reasons_mismatch() -> None:
    replay = make_replay(
        reasons_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="reasons mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_missing_evidence_mismatch() -> None:
    replay = make_replay(
        missing_evidence_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="missing evidence mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_conflicts_mismatch() -> None:
    replay = make_replay(
        conflicts_match=False,
        replay_verified=False,
    )

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="conflicts mismatch",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_non_replay_input() -> None:
    with pytest.raises(TypeError, match="RecoveryDecisionReplay"):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay="RDR-001",  # type: ignore[arg-type]
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_empty_verification_id() -> None:
    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="verification_id",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="",
            replay=make_replay(),
            verified_at=VERIFIED_AT,
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_empty_verifier_id() -> None:
    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="verifier_id",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=make_replay(),
            verified_at=VERIFIED_AT,
            verifier_id="",
        )


def test_verifier_rejects_naive_verification_time() -> None:
    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="timezone-aware",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=make_replay(),
            verified_at=datetime(2026, 7, 14, 12, 0),
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_rejects_verification_before_replay() -> None:
    replay = make_replay()

    with pytest.raises(
        RecoveryDecisionVerificationError,
        match="before replay",
    ):
        RecoveryDecisionVerifier().verify(
            verification_id="RDV-001",
            replay=replay,
            verified_at=datetime(
                2026,
                7,
                14,
                11,
                59,
                59,
                tzinfo=timezone.utc,
            ),
            verifier_id="PROCESS-LINEAGE-CLASSIFIER",
        )


def test_verifier_does_not_mutate_replay() -> None:
    replay = make_replay()
    original = replay

    RecoveryDecisionVerifier().verify(
        verification_id="RDV-001",
        replay=replay,
        verified_at=VERIFIED_AT,
        verifier_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert replay == original


def test_verifier_preserves_observer_only_boundary() -> None:
    result = RecoveryDecisionVerifier().verify(
        verification_id="RDV-001",
        replay=make_replay(),
        verified_at=VERIFIED_AT,
        verifier_id="PROCESS-LINEAGE-CLASSIFIER",
    )

    assert result.execution_requested is False
    assert result.side_effects_permitted is False