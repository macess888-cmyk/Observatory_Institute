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


class CloneClassificationError(ValueError):
    """Raised when events do not form a valid clone transition."""


class CloneClassifier:
    """Classifies clone transitions from one parent into multiple children."""

    RULE_ID = "CL-001"

    def classify(
        self,
        parent: ProcessEvent,
        children: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        if not isinstance(parent, ProcessEvent):
            raise TypeError("parent must be a ProcessEvent.")

        if not isinstance(children, tuple):
            raise TypeError("children must be a tuple.")

        if any(not isinstance(child, ProcessEvent) for child in children):
            raise TypeError(
                "children must contain only ProcessEvent instances."
            )

        if len(children) < 2:
            raise CloneClassificationError(
                "Clone classification requires at least two child events."
            )

        self._validate_children(parent, children)

        authority_roles = [
            child.authority_role
            for child in children
        ]
        primary_count = authority_roles.count("PRIMARY")
        has_authority_collision = primary_count > 1

        if has_authority_collision:
            return self._build_collision_result(parent, children)

        return self._build_valid_result(parent, children)

    def _validate_children(
        self,
        parent: ProcessEvent,
        children: tuple[ProcessEvent, ...],
    ) -> None:
        runtime_ids: set[str] = set()
        execution_ids: set[str] = set()
        state_ids: set[str] = set()
        branch_ids: set[str] = set()
        snapshot_ids: set[str] = set()

        for child in children:
            if child.event_type is not EventType.CLONE:
                raise CloneClassificationError(
                    "Every child event must use EventType.CLONE."
                )

            if parent.event_id not in child.parent_event_ids:
                raise CloneClassificationError(
                    "Every clone must reference the parent event."
                )

            if child.sequence_number <= parent.sequence_number:
                raise CloneClassificationError(
                    "Clone sequence must follow the parent event."
                )

            if child.service_id != parent.service_id:
                raise CloneClassificationError(
                    "Service identity must remain unchanged."
                )

            if parent.state_id not in child.parent_state_ids:
                raise CloneClassificationError(
                    "Every clone must reference the parent state."
                )

            if not child.snapshot_id:
                raise CloneClassificationError(
                    "Every clone requires a snapshot identity."
                )

            if not child.evidence_ids:
                raise CloneClassificationError(
                    "Every clone requires snapshot evidence."
                )

            if not child.branch_id:
                raise CloneClassificationError(
                    "Every clone requires a branch identity."
                )

            runtime_ids.add(child.runtime_id)
            execution_ids.add(child.execution_id)
            state_ids.add(child.state_id)
            branch_ids.add(child.branch_id)
            snapshot_ids.add(child.snapshot_id)

        if len(runtime_ids) != len(children):
            raise CloneClassificationError(
                "Clone children must have distinct runtime identities."
            )

        if len(execution_ids) != len(children):
            raise CloneClassificationError(
                "Clone children must have distinct execution identities."
            )

        if len(state_ids) != len(children):
            raise CloneClassificationError(
                "Clone children must have distinct state identities."
            )

        if len(branch_ids) != len(children):
            raise CloneClassificationError(
                "Clone children must have distinct branch identities."
            )

        if len(snapshot_ids) != 1:
            raise CloneClassificationError(
                "Clone children must share the same snapshot identity."
            )

    def _build_valid_result(
        self,
        parent: ProcessEvent,
        children: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        child_ids = ", ".join(
            child.event_id
            for child in children
        )

        return ContinuityClassification(
            transition_id=f"{parent.event_id}->{child_ids}",
            event_type=EventType.CLONE,
            service_continuity=ContinuityStatus.CONTINUOUS,
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
            state_lineage=LineageStatus.SHARED_PARENT,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.CLONED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.RULE_ID,),
            reasons=(
                "The clone children preserve the logical service identity.",
                "Each child has a distinct runtime identity.",
                "Each child has a distinct execution identity.",
                "The clone children share the same parent state and "
                "snapshot identity.",
                "The resulting state lineages have a shared parent.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _build_collision_result(
        self,
        parent: ProcessEvent,
        children: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        child_ids = ", ".join(
            child.event_id
            for child in children
        )

        return ContinuityClassification(
            transition_id=f"{parent.event_id}->{child_ids}",
            event_type=EventType.CLONE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.SHARED_PARENT,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.CLONED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.RULE_ID,),
            reasons=(
                "The clone children have distinct runtime and execution "
                "identities.",
                "The clone children share the same parent state and "
                "snapshot identity.",
                "Multiple clone children claim the exclusive PRIMARY role.",
            ),
            missing_evidence=(),
            conflicts=(
                "Authority collision detected across clone children.",
            ),
        )