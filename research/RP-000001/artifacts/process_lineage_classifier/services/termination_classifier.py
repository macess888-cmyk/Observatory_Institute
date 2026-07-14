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


class TerminationClassificationError(ValueError):
    """Raised when events do not form a valid termination transition."""


class TerminationClassifier:
    """Classifies verified, unverified, and conflicted terminations."""

    VERIFIED_TERMINATION_RULE = "TM-001"
    UNVERIFIED_TERMINATION_RULE = "TM-002"
    AUTHORITY_CONFLICT_RULE = "TM-003"

    VERIFIED_EVIDENCE_HINTS = (
        "TERMINATION",
        "EXECUTION-STOP",
        "AUTHORITY-REVOCATION",
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
        if current.event_type is not EventType.TERMINATE:
            raise TerminationClassificationError(
                "Current event must use EventType.TERMINATE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise TerminationClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise TerminationClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise TerminationClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise TerminationClassificationError(
                "Runtime identity must remain unchanged at termination."
            )

        if current.execution_id != previous.execution_id:
            raise TerminationClassificationError(
                "Execution identity must remain unchanged at termination."
            )

        if current.state_id != previous.state_id:
            raise TerminationClassificationError(
                "State identity must remain unchanged at termination."
            )

        if previous.state_id not in current.parent_state_ids:
            raise TerminationClassificationError(
                "Termination must reference the previous state as a parent."
            )

        has_authority_conflict = any(
            self.AUTHORITY_CONFLICT_HINT in evidence_id.upper()
            for evidence_id in current.evidence_ids
        )

        if current.authority_role != "NONE" and not has_authority_conflict:
            raise TerminationClassificationError(
                "Terminated runtime must use the NONE authority role."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.TERMINATE,
            service_continuity=ContinuityStatus.TERMINATED,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.TERMINATED,
            authority_continuity=ContinuityStatus.TERMINATED,
            availability_continuity=ContinuityStatus.TERMINATED,
            state_lineage=LineageStatus.DISCONTINUOUS,
            binding_status=BindingStatus.EXPIRED,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.TERMINATED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_TERMINATION_RULE,),
            reasons=(
                "The runtime was explicitly terminated.",
                "The execution was explicitly stopped.",
                "Authority was revoked from the terminated runtime.",
                "Service availability ended at this transition boundary.",
                "The prior state lineage does not continue through termination.",
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
            event_type=EventType.TERMINATE,
            service_continuity=ContinuityStatus.UNVERIFIED,
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.UNVERIFIED,
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.TERMINATED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_TERMINATION_RULE,),
            reasons=(
                "A termination transition was declared.",
                "Runtime, execution, and state identifiers remained stable.",
                "Required termination evidence was incomplete.",
                "Termination and authority revocation cannot be admitted.",
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
            event_type=EventType.TERMINATE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.TERMINATED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.UNKNOWN,
            state_lineage=LineageStatus.DISCONTINUOUS,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.TERMINATED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.AUTHORITY_CONFLICT_RULE,),
            reasons=(
                "Termination and execution-stop evidence were supplied.",
                "The runtime still claims an active authority role.",
                "Authority revocation is contradicted by the active role claim.",
                "Exclusive authority cannot be resolved at termination.",
            ),
            missing_evidence=(),
            conflicts=(
                "Authority remains active after declared termination.",
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