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
from models import ContinuityClassification, ProcessEvent


class RollbackRecoveryClassificationError(ValueError):
    """Raised when events do not form a valid rollback-recovery transition."""


class RollbackRecoveryClassifier:
    """Classifies verified, incomplete, conflicted, and stale recovery."""

    VERIFIED_RECOVERY_RULE = "RKR-001"
    UNVERIFIED_RECOVERY_RULE = "RKR-002"
    INTEGRITY_CONFLICT_RULE = "RKR-003"
    STALE_RECOVERY_RULE = "RKR-004"

    ROLLBACK_RECOVERY_HINT = "ROLLBACK-RECOVERY"
    FORWARD_STATE_VERIFY_HINT = "FORWARD-STATE-VERIFY"
    INTEGRITY_CHECK_HINT = "INTEGRITY-CHECK"
    AUTHORITY_PRESERVE_HINT = "AUTHORITY-PRESERVE"
    RECOVERY_COMPLETE_HINT = "RECOVERY-COMPLETE"
    INTEGRITY_CONFLICT_HINT = "INTEGRITY-CONFLICT"
    STALE_RECOVERY_HINT = "STALE-RECOVERY-STATE"

    def classify(
        self,
        rollback: ProcessEvent,
        recovered: ProcessEvent,
    ) -> ContinuityClassification:
        if not isinstance(rollback, ProcessEvent):
            raise TypeError("rollback must be a ProcessEvent.")

        if not isinstance(recovered, ProcessEvent):
            raise TypeError("recovered must be a ProcessEvent.")

        self._validate_transition(rollback, recovered)

        normalized_evidence = self._normalized_evidence(recovered)

        if self._contains_hint(
            normalized_evidence,
            self.INTEGRITY_CONFLICT_HINT,
        ):
            return self._classify_integrity_conflict(
                rollback,
                recovered,
            )

        if self._contains_hint(
            normalized_evidence,
            self.STALE_RECOVERY_HINT,
        ):
            return self._classify_stale(
                rollback,
                recovered,
            )

        missing_evidence = self._find_missing_evidence(
            normalized_evidence
        )

        if missing_evidence:
            return self._classify_unverified(
                rollback,
                recovered,
                missing_evidence,
            )

        return self._classify_verified(
            rollback,
            recovered,
        )

    def _validate_transition(
        self,
        rollback: ProcessEvent,
        recovered: ProcessEvent,
    ) -> None:
        if recovered.event_type is not EventType.ROLLBACK_RECOVERY:
            raise RollbackRecoveryClassificationError(
                "Current event must use EventType.ROLLBACK_RECOVERY."
            )

        if rollback.event_id not in recovered.parent_event_ids:
            raise RollbackRecoveryClassificationError(
                "Recovery must reference the rollback event as a parent."
            )

        if recovered.sequence_number <= rollback.sequence_number:
            raise RollbackRecoveryClassificationError(
                "Recovery sequence must follow the rollback sequence."
            )

        if recovered.service_id != rollback.service_id:
            raise RollbackRecoveryClassificationError(
                "Service identity must remain unchanged."
            )

        if recovered.runtime_id != rollback.runtime_id:
            raise RollbackRecoveryClassificationError(
                "Runtime identity must remain unchanged during rollback recovery."
            )

        if recovered.execution_id != rollback.execution_id:
            raise RollbackRecoveryClassificationError(
                "Execution identity must remain unchanged during rollback recovery."
            )

        if recovered.host_id != rollback.host_id:
            raise RollbackRecoveryClassificationError(
                "Host identity must remain unchanged during rollback recovery."
            )

        if recovered.address != rollback.address:
            raise RollbackRecoveryClassificationError(
                "Address must remain unchanged during rollback recovery."
            )

        if recovered.authority_role != rollback.authority_role:
            raise RollbackRecoveryClassificationError(
                "Authority role must remain unchanged during rollback recovery."
            )

        if rollback.state_id not in recovered.parent_state_ids:
            raise RollbackRecoveryClassificationError(
                "Recovery must reference the rollback state as a parent state."
            )

        if recovered.state_id == rollback.state_id:
            raise RollbackRecoveryClassificationError(
                "Recovery must advance to a new forward state identity."
            )

        if not recovered.snapshot_id:
            raise RollbackRecoveryClassificationError(
                "Rollback recovery requires a snapshot identity."
            )

    def _classify_verified(
        self,
        rollback: ProcessEvent,
        recovered: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{rollback.event_id}->{recovered.event_id}",
            event_type=EventType.ROLLBACK_RECOVERY,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.RECONCILED,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.ROLLBACK_RECOVERED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_RECOVERY_RULE,),
            reasons=(
                "The rollback baseline was explicitly verified.",
                "A new forward state was established after rollback.",
                "Forward state verification supports the recovered state.",
                "Integrity checks passed for the recovery result.",
                "Authority remained preserved during recovery.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _classify_unverified(
        self,
        rollback: ProcessEvent,
        recovered: ProcessEvent,
        missing_evidence: tuple[str, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{rollback.event_id}->{recovered.event_id}",
            event_type=EventType.ROLLBACK_RECOVERY,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.ROLLBACK_RECOVERED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_RECOVERY_RULE,),
            reasons=(
                "A rollback-recovery transition was declared.",
                "Runtime and execution identities remained unchanged.",
                "Required rollback-recovery evidence is incomplete.",
                "Forward state integrity and authority preservation "
                "cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_integrity_conflict(
        self,
        rollback: ProcessEvent,
        recovered: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{rollback.event_id}->{recovered.event_id}",
            event_type=EventType.ROLLBACK_RECOVERY,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONFLICTED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.CONFLICTED,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.ROLLBACK_RECOVERED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.INTEGRITY_CONFLICT_RULE,),
            reasons=(
                "A rollback-recovery transition was declared.",
                "A forward state was produced after rollback.",
                "Integrity evidence conflicts with the recovered state.",
                "The recovery result cannot be admitted.",
            ),
            missing_evidence=(),
            conflicts=(
                "Recovered forward-state integrity conflict detected.",
            ),
        )

    def _classify_stale(
        self,
        rollback: ProcessEvent,
        recovered: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{rollback.event_id}->{recovered.event_id}",
            event_type=EventType.ROLLBACK_RECOVERY,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.DEGRADED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.DISCONTINUOUS,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.ROLLBACK_RECOVERED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.STALE_RECOVERY_RULE,),
            reasons=(
                "A rollback-recovery transition was declared.",
                "Runtime and execution identities remained unchanged.",
                "The recovered state is older than the required forward state.",
                "Stale recovery evidence prevents lineage reconciliation.",
            ),
            missing_evidence=(),
            conflicts=(
                "The recovered state is stale relative to the expected "
                "forward state.",
            ),
        )

    def _find_missing_evidence(
        self,
        normalized_evidence: tuple[str, ...],
    ) -> tuple[str, ...]:
        missing: list[str] = []

        for hint, description in (
            (
                self.ROLLBACK_RECOVERY_HINT,
                "rollback recovery evidence",
            ),
            (
                self.FORWARD_STATE_VERIFY_HINT,
                "forward state verification evidence",
            ),
            (
                self.INTEGRITY_CHECK_HINT,
                "integrity check evidence",
            ),
            (
                self.AUTHORITY_PRESERVE_HINT,
                "authority preservation evidence",
            ),
            (
                self.RECOVERY_COMPLETE_HINT,
                "recovery completion evidence",
            ),
        ):
            if not self._contains_hint(
                normalized_evidence,
                hint,
            ):
                missing.append(description)

        return tuple(missing)

    @staticmethod
    def _normalized_evidence(
        event: ProcessEvent,
    ) -> tuple[str, ...]:
        return tuple(
            evidence_id.upper()
            for evidence_id in event.evidence_ids
        )

    @staticmethod
    def _contains_hint(
        evidence: tuple[str, ...],
        hint: str,
    ) -> bool:
        return any(
            hint in evidence_id
            for evidence_id in evidence
        )