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


class RestoreClassificationError(ValueError):
    """Raised when events do not form a valid restore transition."""


class RestoreClassifier:
    """Classifies verified restore transitions."""

    RULE_ID = "RT-001"

    REQUIRED_EVIDENCE_HINTS = (
        "SNAPSHOT",
        "STATE-VERIFY",
    )

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

        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.RESTORE,
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
            transition_status=TransitionStatus.RESTORED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.RULE_ID,),
            reasons=(
                "The logical service identity remained unchanged.",
                "The previous runtime terminated and a new runtime began.",
                "The previous execution terminated and a new execution began.",
                "The prior state was restored from an explicit snapshot.",
                "State verification evidence supports the restored lineage.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _validate_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> None:
        if current.event_type is not EventType.RESTORE:
            raise RestoreClassificationError(
                "Current event must use EventType.RESTORE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise RestoreClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise RestoreClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise RestoreClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id == previous.runtime_id:
            raise RestoreClassificationError(
                "Runtime identity must change during restore."
            )

        if current.execution_id == previous.execution_id:
            raise RestoreClassificationError(
                "Execution identity must change during restore."
            )

        if current.authority_role != previous.authority_role:
            raise RestoreClassificationError(
                "Authority role must remain unchanged for version 0.1."
            )

        if not current.snapshot_id:
            raise RestoreClassificationError(
                "Restore transition requires snapshot evidence."
            )

        if not current.parent_state_ids:
            raise RestoreClassificationError(
                "Restore transition requires parent state evidence."
            )

        if previous.state_id not in current.parent_state_ids:
            raise RestoreClassificationError(
                "Restore transition must reference the previous state."
            )

        if current.state_id != previous.state_id:
            raise RestoreClassificationError(
                "Restored state identity must match the previous state."
            )

        normalized_evidence = tuple(
            evidence_id.upper()
            for evidence_id in current.evidence_ids
        )

        missing_evidence = [
            hint
            for hint in self.REQUIRED_EVIDENCE_HINTS
            if not any(
                hint in evidence_id
                for evidence_id in normalized_evidence
            )
        ]

        if missing_evidence:
            raise RestoreClassificationError(
                "Restore transition requires snapshot and state verification "
                "evidence."
            )