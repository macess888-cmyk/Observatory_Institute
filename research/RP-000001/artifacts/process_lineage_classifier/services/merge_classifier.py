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


class MergeClassificationError(ValueError):
    """Raised when events do not form a valid merge transition."""


class MergeClassifier:
    """Classifies multiple parent lineages merging into one successor."""

    RULE_ID = "MR-001"

    REQUIRED_EVIDENCE_HINTS = (
        "MERGE",
        "STATE-RECONCILE",
    )

    def classify(
        self,
        parents: tuple[ProcessEvent, ...],
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if not isinstance(parents, tuple):
            raise TypeError("parents must be a tuple.")

        if any(not isinstance(parent, ProcessEvent) for parent in parents):
            raise TypeError(
                "parents must contain only ProcessEvent instances."
            )

        if not isinstance(current, ProcessEvent):
            raise TypeError("current must be a ProcessEvent.")

        if len(parents) < 2:
            raise MergeClassificationError(
                "Merge classification requires at least two parent events."
            )

        self._validate_transition(parents, current)

        parent_ids = ", ".join(parent.event_id for parent in parents)

        return ContinuityClassification(
            transition_id=f"{parent_ids}->{current.event_id}",
            event_type=EventType.MERGE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.MERGED,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.MERGED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.RULE_ID,),
            reasons=(
                "The merged event preserves the logical service identity.",
                "The merged state preserves multiple parent lineages.",
                "The merge creates a new state identity.",
                "The merge creates a new runtime and execution identity.",
                "Merge and state reconciliation evidence were supplied.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _validate_transition(
        self,
        parents: tuple[ProcessEvent, ...],
        current: ProcessEvent,
    ) -> None:
        if current.event_type is not EventType.MERGE:
            raise MergeClassificationError(
                "Current event must use EventType.MERGE."
            )

        parent_event_ids = {parent.event_id for parent in parents}
        current_parent_event_ids = set(current.parent_event_ids)

        if parent_event_ids != current_parent_event_ids:
            raise MergeClassificationError(
                "Merge must reference every parent event."
            )

        parent_state_ids = {parent.state_id for parent in parents}
        current_parent_state_ids = set(current.parent_state_ids)

        if parent_state_ids != current_parent_state_ids:
            raise MergeClassificationError(
                "Merge must reference every parent state."
            )

        service_ids = {parent.service_id for parent in parents}

        if len(service_ids) != 1:
            raise MergeClassificationError(
                "All parent events must share one service identity."
            )

        parent_service_id = next(iter(service_ids))

        if current.service_id != parent_service_id:
            raise MergeClassificationError(
                "Service identity must remain unchanged."
            )

        if current.sequence_number <= max(
            parent.sequence_number for parent in parents
        ):
            raise MergeClassificationError(
                "Merge sequence must follow every parent event."
            )

        parent_runtime_ids = {parent.runtime_id for parent in parents}

        if current.runtime_id in parent_runtime_ids:
            raise MergeClassificationError(
                "Merge must create a new runtime identity."
            )

        parent_execution_ids = {
            parent.execution_id
            for parent in parents
        }

        if current.execution_id in parent_execution_ids:
            raise MergeClassificationError(
                "Merge must create a new execution identity."
            )

        if current.state_id in parent_state_ids:
            raise MergeClassificationError(
                "Merge must create a new state identity."
            )

        if not current.merge_id:
            raise MergeClassificationError(
                "Merge transition requires a merge identity."
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
            raise MergeClassificationError(
                "Merge transition requires merge and state reconciliation "
                "evidence."
            )