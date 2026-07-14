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


class RebindingClassificationError(ValueError):
    """Raised when events do not form a valid rebinding transition."""


class RebindingClassifier:
    """Classifies verified, unverified, and conflicted rebindings."""

    VERIFIED_REBINDING_RULE = "RB-001"
    UNVERIFIED_REBINDING_RULE = "RB-002"
    BINDING_COLLISION_RULE = "RB-003"

    VERIFIED_EVIDENCE_HINTS = (
        "REBINDING",
        "TARGET-RESOLUTION",
        "OLD-BINDING-RELEASE",
    )

    BINDING_COLLISION_HINT = "BINDING-COLLISION"

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
            self.BINDING_COLLISION_HINT in evidence_id
            for evidence_id in normalized_evidence
        ):
            return self._classify_collision(previous, current)

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
        if current.event_type is not EventType.REBIND:
            raise RebindingClassificationError(
                "Current event must use EventType.REBIND."
            )

        if previous.event_id not in current.parent_event_ids:
            raise RebindingClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise RebindingClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise RebindingClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise RebindingClassificationError(
                "Runtime identity must remain unchanged during rebinding."
            )

        if current.execution_id != previous.execution_id:
            raise RebindingClassificationError(
                "Execution identity must remain unchanged during rebinding."
            )

        if current.state_id != previous.state_id:
            raise RebindingClassificationError(
                "State identity must remain unchanged during rebinding."
            )

        if current.authority_role != previous.authority_role:
            raise RebindingClassificationError(
                "Authority role must remain unchanged during rebinding."
            )

        if previous.state_id not in current.parent_state_ids:
            raise RebindingClassificationError(
                "Rebinding must reference the previous state as a parent."
            )

        if current.address == previous.address:
            raise RebindingClassificationError(
                "Address must change during rebinding."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.REBIND,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.REBOUND,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_REBINDING_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "The runtime, execution, and state identities remained stable.",
                f"The address changed from {previous.address} "
                f"to {current.address}.",
                "Target-resolution evidence supports the new binding.",
                "Old-binding release evidence prevents simultaneous binding.",
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
            event_type=EventType.REBIND,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.REBOUND,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_REBINDING_RULE,),
            reasons=(
                "A rebinding transition was declared.",
                "Runtime, execution, and state identities remained stable.",
                "The address changed.",
                "Required rebinding evidence was incomplete.",
                "The new binding cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_collision(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.REBIND,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.REBOUND,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.BINDING_COLLISION_RULE,),
            reasons=(
                "A rebinding transition was declared.",
                "Runtime, execution, and state identities remained stable.",
                "The new address resolved successfully.",
                "Evidence indicates that another active binding remains.",
                "Exclusive binding cannot be admitted.",
            ),
            missing_evidence=(),
            conflicts=(
                "Binding collision detected at the target address.",
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