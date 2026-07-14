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


class LineageReconciliationClassificationError(ValueError):
    """Raised when events cannot form a lineage-reconciliation assessment."""


class LineageReconciliationClassifier:
    """Classifies verified, incomplete, conflicted, and partial reconciliation."""

    VERIFIED_RECONCILIATION_RULE = "LR-001"
    UNVERIFIED_RECONCILIATION_RULE = "LR-002"
    UNRESOLVED_CONFLICT_RULE = "LR-003"
    MISSING_PARENT_STATE_RULE = "LR-004"

    LINEAGE_RECONCILIATION_HINT = "LINEAGE-RECONCILIATION"
    STATE_MERGE_VERIFY_HINT = "STATE-MERGE-VERIFY"
    CONFLICT_RESOLUTION_HINT = "CONFLICT-RESOLUTION"
    QUORUM_CONFIRMATION_HINT = "QUORUM-CONFIRMATION"
    LINEAGE_ACK_HINT = "LINEAGE-ACK"
    PARENT_STATE_VERIFY_HINT = "PARENT-STATE-VERIFY"
    UNRESOLVED_CONFLICT_HINT = "UNRESOLVED-CONFLICT"

    def classify(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        if not isinstance(events, tuple):
            raise TypeError("events must be a tuple.")

        if any(
            not isinstance(event, ProcessEvent)
            for event in events
        ):
            raise TypeError(
                "events must contain only ProcessEvent instances."
            )

        if len(events) < 3:
            raise LineageReconciliationClassificationError(
                "Lineage reconciliation requires at least three events."
            )

        self._validate_events(events)

        parent_events = events[:-1]
        reconciled_event = events[-1]

        if self._has_unresolved_conflict(reconciled_event):
            return self._classify_conflict(events)

        missing_parent_states = self._find_missing_parent_states(
            parent_events,
            reconciled_event,
        )

        if missing_parent_states:
            return self._classify_missing_parent_state(
                events,
                missing_parent_states,
            )

        missing_evidence = self._find_missing_evidence(
            parent_events,
            reconciled_event,
        )

        if missing_evidence:
            return self._classify_unverified(
                events,
                missing_evidence,
            )

        return self._classify_verified(events)

    def _validate_events(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        service_ids = {
            event.service_id
            for event in events
        }

        if len(service_ids) != 1:
            raise LineageReconciliationClassificationError(
                "All events must share one service identity."
            )

        event_ids = [
            event.event_id
            for event in events
        ]

        if len(set(event_ids)) != len(event_ids):
            raise LineageReconciliationClassificationError(
                "Duplicate event identity detected."
            )

        runtime_ids = [
            event.runtime_id
            for event in events
        ]

        if len(set(runtime_ids)) != len(runtime_ids):
            raise LineageReconciliationClassificationError(
                "Duplicate runtime identity detected."
            )

        execution_ids = [
            event.execution_id
            for event in events
        ]

        if len(set(execution_ids)) != len(execution_ids):
            raise LineageReconciliationClassificationError(
                "Duplicate execution identity detected."
            )

        sequence_numbers = [
            event.sequence_number
            for event in events
        ]

        if sequence_numbers != sorted(sequence_numbers):
            raise LineageReconciliationClassificationError(
                "Event sequence numbers must be increasing."
            )

        if len(set(sequence_numbers)) != len(sequence_numbers):
            raise LineageReconciliationClassificationError(
                "Event sequence numbers must be distinct and increasing."
            )

    def _classify_verified(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.LINEAGE_RECONCILIATION,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            execution_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.RECONCILED,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.LINEAGE_RECONCILED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_RECONCILIATION_RULE,),
            reasons=(
                "All parent states were explicitly referenced.",
                "Parent state evidence was independently verified.",
                "Divergent lineages were reconciled into a new state.",
                "Conflict-resolution evidence supports the merged lineage.",
                "Quorum confirmation supports the reconciliation result.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _classify_unverified(
        self,
        events: tuple[ProcessEvent, ...],
        missing_evidence: tuple[str, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.LINEAGE_RECONCILIATION,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.LINEAGE_RECONCILED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_RECONCILIATION_RULE,),
            reasons=(
                "A lineage-reconciliation transition was declared.",
                "Multiple parent lineages were referenced.",
                "Required reconciliation evidence is incomplete.",
                "The merged state and conflict resolution cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_conflict(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.LINEAGE_RECONCILIATION,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            execution_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_continuity=ContinuityStatus.CONFLICTED,
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.CONFLICTED,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.LINEAGE_RECONCILED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.UNRESOLVED_CONFLICT_RULE,),
            reasons=(
                "A lineage-reconciliation transition was declared.",
                "Multiple parent states were referenced.",
                "Evidence indicates that a lineage conflict remains unresolved.",
                "The reconciled state cannot be admitted.",
            ),
            missing_evidence=(),
            conflicts=(
                "Unresolved lineage conflict remains after reconciliation.",
            ),
        )

    def _classify_missing_parent_state(
        self,
        events: tuple[ProcessEvent, ...],
        missing_parent_states: tuple[str, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.LINEAGE_RECONCILIATION,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.LINEAGE_RECONCILED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.MISSING_PARENT_STATE_RULE,),
            reasons=(
                "A lineage-reconciliation transition was declared.",
                "One or more source states were omitted from the reconciliation.",
                "Complete parent-state coverage cannot be established.",
                "The reconciled lineage cannot be admitted.",
            ),
            missing_evidence=missing_parent_states,
            conflicts=(),
        )

    def _find_missing_parent_states(
        self,
        parent_events: tuple[ProcessEvent, ...],
        reconciled_event: ProcessEvent,
    ) -> tuple[str, ...]:
        referenced_states = set(
            reconciled_event.parent_state_ids
        )

        return tuple(
            f"{parent.state_id} parent state reference"
            for parent in parent_events
            if parent.state_id not in referenced_states
        )

    def _find_missing_evidence(
        self,
        parent_events: tuple[ProcessEvent, ...],
        reconciled_event: ProcessEvent,
    ) -> tuple[str, ...]:
        missing: list[str] = []
        reconciled_evidence = self._normalized_evidence(
            reconciled_event
        )

        for hint, description in (
            (
                self.LINEAGE_RECONCILIATION_HINT,
                "lineage reconciliation evidence",
            ),
            (
                self.STATE_MERGE_VERIFY_HINT,
                "state merge verification evidence",
            ),
            (
                self.CONFLICT_RESOLUTION_HINT,
                "conflict resolution evidence",
            ),
            (
                self.QUORUM_CONFIRMATION_HINT,
                "quorum confirmation evidence",
            ),
        ):
            if not self._contains_hint(
                reconciled_evidence,
                hint,
            ):
                missing.append(description)

        for parent in parent_events:
            parent_evidence = self._normalized_evidence(parent)

            if not self._contains_hint(
                parent_evidence,
                self.PARENT_STATE_VERIFY_HINT,
            ):
                missing.append(
                    f"{parent.event_id} parent state verification"
                )

        for event in (*parent_events, reconciled_event):
            if not self._contains_hint(
                self._normalized_evidence(event),
                self.LINEAGE_ACK_HINT,
            ):
                missing.append(
                    f"{event.event_id} lineage acknowledgement"
                )

        return tuple(missing)

    def _has_unresolved_conflict(
        self,
        reconciled_event: ProcessEvent,
    ) -> bool:
        return self._contains_hint(
            self._normalized_evidence(reconciled_event),
            self.UNRESOLVED_CONFLICT_HINT,
        )

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

    @staticmethod
    def _transition_id(
        events: tuple[ProcessEvent, ...],
    ) -> str:
        event_ids = ",".join(
            event.event_id
            for event in events
        )
        return f"LINEAGE-RECONCILIATION:{event_ids}"