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


class RestartClassificationError(ValueError):
    """Raised when events do not form a valid restart transition."""


class RestartClassifier:
    """Classifies warm and cold restart transitions."""

    WARM_RESTART_RULE = "RS-001"
    COLD_RESTART_RULE = "RS-002"

    def classify(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if not isinstance(previous, ProcessEvent):
            raise TypeError("previous must be a ProcessEvent.")

        if not isinstance(current, ProcessEvent):
            raise TypeError("current must be a ProcessEvent.")

        self._validate_common_transition(previous, current)

        has_restore_markers = bool(
            current.parent_state_ids
            or current.evidence_ids
            or current.snapshot_id
        )

        if has_restore_markers:
            return self._classify_warm_restart(previous, current)

        return self._classify_cold_restart(previous, current)

    def _validate_common_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> None:
        if current.event_type is not EventType.RESTART:
            raise RestartClassificationError(
                "Current event must use EventType.RESTART."
            )

        if previous.event_id not in current.parent_event_ids:
            raise RestartClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise RestartClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise RestartClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id == previous.runtime_id:
            raise RestartClassificationError(
                "Runtime identity must change during restart."
            )

        if current.execution_id == previous.execution_id:
            raise RestartClassificationError(
                "Execution identity must change during restart."
            )

        if current.authority_role != previous.authority_role:
            raise RestartClassificationError(
                "Authority role must remain unchanged for version 0.1."
            )

    def _classify_warm_restart(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if not current.parent_state_ids:
            raise RestartClassificationError(
                "Warm restart requires parent state evidence."
            )

        if previous.state_id not in current.parent_state_ids:
            raise RestartClassificationError(
                "Warm restart evidence must reference the previous state."
            )

        if not current.snapshot_id:
            raise RestartClassificationError(
                "Warm restart requires snapshot evidence."
            )

        if not current.evidence_ids:
            raise RestartClassificationError(
                "Warm restart requires verified restore evidence."
            )

        if current.state_id != previous.state_id:
            raise RestartClassificationError(
                "Warm restart must restore the previous state identity."
            )

        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.RESTART,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.CONDITIONALLY_CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.RESTORED,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.RESTARTED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.WARM_RESTART_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "The previous runtime terminated and a new runtime began.",
                "The previous execution terminated and a new execution began.",
                "The prior state was restored through explicit snapshot "
                "and evidence references.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _classify_cold_restart(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if current.state_id == previous.state_id:
            raise RestartClassificationError(
                "Cold restart must create a new state identity or provide "
                "restore evidence."
            )

        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.RESTART,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.INTERRUPTED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.NEW_ROOT,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.RESTARTED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.COLD_RESTART_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "The previous runtime terminated and a new runtime began.",
                "The previous execution terminated and a new execution began.",
                "No restoration evidence was supplied, so the new state "
                "begins a new lineage root.",
            ),
            missing_evidence=(),
            conflicts=(),
        )