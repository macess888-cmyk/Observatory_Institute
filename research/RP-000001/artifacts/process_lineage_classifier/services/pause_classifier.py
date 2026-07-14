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


class PauseClassificationError(ValueError):
    """Raised when events do not form a valid pause transition."""


class PauseClassifier:
    """Classifies verified, unverified, and conflicted pause transitions."""

    VERIFIED_PAUSE_RULE = "PS-001"
    UNVERIFIED_PAUSE_RULE = "PS-002"
    AUTHORITY_CONFLICT_RULE = "PS-003"

    VERIFIED_EVIDENCE_HINTS = (
        "PAUSE",
        "EXECUTION-SUSPEND",
        "STATE-PRESERVE",
        "AUTHORITY-SUSPEND",
    )

    AUTHORITY_CONFLICT_HINT = "AUTHORITY-STILL-ACTIVE"

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
            self.AUTHORITY_CONFLICT_HINT in evidence_id
            for evidence_id in normalized_evidence
        ):
            return self._classify_authority_conflict(previous, current)

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
        if current.event_type is not EventType.PAUSE:
            raise PauseClassificationError(
                "Current event must use EventType.PAUSE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise PauseClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise PauseClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise PauseClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise PauseClassificationError(
                "Runtime identity must remain unchanged during pause."
            )

        if current.execution_id != previous.execution_id:
            raise PauseClassificationError(
                "Execution identity must remain unchanged during pause."
            )

        if current.state_id != previous.state_id:
            raise PauseClassificationError(
                "State identity must remain unchanged during pause."
            )

        if current.host_id != previous.host_id:
            raise PauseClassificationError(
                "Host identity must remain unchanged during pause."
            )

        if current.address != previous.address:
            raise PauseClassificationError(
                "Address must remain unchanged during pause."
            )

        if previous.state_id not in current.parent_state_ids:
            raise PauseClassificationError(
                "Pause must reference the previous state as a parent."
            )

        has_authority_conflict = any(
            self.AUTHORITY_CONFLICT_HINT in evidence_id.upper()
            for evidence_id in current.evidence_ids
        )

        if current.authority_role != "NONE" and not has_authority_conflict:
            raise PauseClassificationError(
                "Paused runtime must use the NONE authority role."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.PAUSE,
            service_continuity=ContinuityStatus.INTERRUPTED,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.INTERRUPTED,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.INTERRUPTED,
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.SUSPENDED,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.PAUSED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_PAUSE_RULE,),
            reasons=(
                "The runtime identity remained continuous during pause.",
                "Execution was suspended without replacing the execution identity.",
                "State was preserved without creating a new lineage.",
                "Authority was suspended while the process was paused.",
                "Service availability was interrupted during the pause interval.",
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
            event_type=EventType.PAUSE,
            service_continuity=ContinuityStatus.UNVERIFIED,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.UNKNOWN,
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.PAUSED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_PAUSE_RULE,),
            reasons=(
                "A pause transition was declared.",
                "The runtime identity remained unchanged.",
                "Required pause evidence was incomplete.",
                "Execution suspension, state preservation, and authority "
                "suspension cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_authority_conflict(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.PAUSE,
            service_continuity=ContinuityStatus.INTERRUPTED,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.INTERRUPTED,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.PAUSED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.AUTHORITY_CONFLICT_RULE,),
            reasons=(
                "Execution was suspended and state was preserved.",
                "The runtime remained present during pause.",
                "The paused runtime still claims an active authority role.",
                "Authority suspension cannot be admitted while the role "
                "remains active.",
            ),
            missing_evidence=(),
            conflicts=(
                "Authority remains active during the declared pause.",
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