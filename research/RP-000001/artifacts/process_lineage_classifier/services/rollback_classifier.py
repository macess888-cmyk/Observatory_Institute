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


class RollbackClassificationError(ValueError):
    """Raised when events do not form a valid rollback transition."""


class RollbackClassifier:
    """Classifies verified, unverified, and conflicted rollbacks."""

    VERIFIED_ROLLBACK_RULE = "RK-001"
    UNVERIFIED_ROLLBACK_RULE = "RK-002"
    ROLLBACK_CONFLICT_RULE = "RK-003"

    VERIFIED_EVIDENCE_HINTS = (
        "ROLLBACK",
        "SNAPSHOT-VERIFY",
        "TARGET-STATE-VERIFY",
        "AUTHORITY-PRESERVE",
    )

    CONFLICT_EVIDENCE_HINT = "TARGET-STATE-CONFLICT"

    def classify(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if not isinstance(previous, ProcessEvent):
            raise TypeError("previous must be a ProcessEvent.")

        if not isinstance(current, ProcessEvent):
            raise TypeError("current must be a ProcessEvent.")

        self._validate_transition(previous, current)

        normalized_evidence = tuple(
            evidence_id.upper()
            for evidence_id in current.evidence_ids
        )

        if any(
            self.CONFLICT_EVIDENCE_HINT in evidence_id
            for evidence_id in normalized_evidence
        ):
            return self._classify_conflict(previous, current)

        missing_evidence = self._find_missing_evidence(
            normalized_evidence
        )

        if missing_evidence:
            return self._classify_unverified(
                previous,
                current,
                missing_evidence,
            )

        return self._classify_verified(previous, current)

    def _validate_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> None:
        if current.event_type is not EventType.ROLLBACK:
            raise RollbackClassificationError(
                "Current event must use EventType.ROLLBACK."
            )

        if previous.event_id not in current.parent_event_ids:
            raise RollbackClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise RollbackClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise RollbackClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise RollbackClassificationError(
                "Runtime identity must remain unchanged during rollback."
            )

        if current.execution_id != previous.execution_id:
            raise RollbackClassificationError(
                "Execution identity must remain unchanged during rollback."
            )

        if current.authority_role != previous.authority_role:
            raise RollbackClassificationError(
                "Authority role must remain unchanged during rollback."
            )

        if current.state_id == previous.state_id:
            raise RollbackClassificationError(
                "Rollback must restore a different prior state identity."
            )

        if previous.state_id not in current.parent_state_ids:
            raise RollbackClassificationError(
                "Rollback must reference the current pre-rollback state."
            )

        if current.state_id not in current.parent_state_ids:
            raise RollbackClassificationError(
                "Rollback must reference the restored target state."
            )

        if not current.snapshot_id:
            raise RollbackClassificationError(
                "Rollback requires a snapshot identity."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.ROLLBACK,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.DEGRADED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.RESTORED,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.ROLLED_BACK,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_ROLLBACK_RULE,),
            reasons=(
                "A rollback transition restored an earlier state.",
                "The runtime and execution identities remained unchanged.",
                "Snapshot verification supports the rollback target.",
                "The restored state differs from the pre-rollback state.",
                "Authority remained preserved during rollback.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _classify_unverified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
        missing_evidence: tuple[str, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.ROLLBACK,
            service_continuity=ContinuityStatus.CONTINUOUS,
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
            transition_status=TransitionStatus.ROLLED_BACK,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_ROLLBACK_RULE,),
            reasons=(
                "A rollback transition was declared.",
                "Runtime and execution identities remained unchanged.",
                "Required rollback evidence was incomplete.",
                "The restored state and authority preservation cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_conflict(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.ROLLBACK,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.CONFLICTED,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.ROLLED_BACK,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.ROLLBACK_CONFLICT_RULE,),
            reasons=(
                "A rollback transition was declared.",
                "Runtime and execution identities remained unchanged.",
                "Snapshot evidence identifies a rollback target.",
                "Target-state evidence conflicts with the declared restored state.",
                "The rollback result cannot be admitted.",
            ),
            missing_evidence=(),
            conflicts=(
                "Rollback target-state conflict detected.",
            ),
        )

    def _find_missing_evidence(
        self,
        normalized_evidence: tuple[str, ...],
    ) -> tuple[str, ...]:
        missing: list[str] = []

        for hint in self.VERIFIED_EVIDENCE_HINTS:
            if not any(hint in item for item in normalized_evidence):
                missing.append(
                    hint.lower().replace("-", " ") + " evidence"
                )

        return tuple(missing)