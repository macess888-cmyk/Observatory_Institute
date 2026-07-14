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


class SplitBrainClassificationError(ValueError):
    """Raised when events cannot form a valid split-brain assessment."""


class SplitBrainClassifier:
    """Classifies confirmed, unverified, and clear authority topology."""

    CONFIRMED_SPLIT_BRAIN_RULE = "SB-001"
    UNVERIFIED_SPLIT_BRAIN_RULE = "SB-002"
    CLEAR_AUTHORITY_RULE = "SB-003"

    PRIMARY_EVIDENCE_HINT = "ACTIVE-PRIMARY"
    VALID_LEASE_HINT = "LEASE-VALID"

    def classify(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        if not isinstance(events, tuple):
            raise TypeError("events must be a tuple.")

        if any(not isinstance(event, ProcessEvent) for event in events):
            raise TypeError(
                "events must contain only ProcessEvent instances."
            )

        if len(events) < 2:
            raise SplitBrainClassificationError(
                "Split-brain classification requires at least two events."
            )

        self._validate_events(events)

        primary_events = tuple(
            event
            for event in events
            if event.authority_role == "PRIMARY"
        )

        if len(primary_events) <= 1:
            return self._classify_clear(events)

        missing_evidence = self._find_missing_evidence(primary_events)

        if missing_evidence:
            return self._classify_unverified(
                events,
                missing_evidence,
            )

        return self._classify_confirmed(events)

    def _validate_events(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> None:
        service_ids = {event.service_id for event in events}

        if len(service_ids) != 1:
            raise SplitBrainClassificationError(
                "All events must share one service identity."
            )

        event_ids = [event.event_id for event in events]

        if len(set(event_ids)) != len(event_ids):
            raise SplitBrainClassificationError(
                "Every event must have a distinct event identity."
            )

        runtime_ids = [event.runtime_id for event in events]

        if len(set(runtime_ids)) != len(runtime_ids):
            raise SplitBrainClassificationError(
                "Every event must have a distinct runtime identity."
            )

        execution_ids = [event.execution_id for event in events]

        if len(set(execution_ids)) != len(execution_ids):
            raise SplitBrainClassificationError(
                "Every event must have a distinct execution identity."
            )

        sequence_numbers = [
            event.sequence_number
            for event in events
        ]

        if sequence_numbers != sorted(sequence_numbers):
            raise SplitBrainClassificationError(
                "Event sequence numbers must be increasing."
            )

        if len(set(sequence_numbers)) != len(sequence_numbers):
            raise SplitBrainClassificationError(
                "Event sequence numbers must be distinct and increasing."
            )

    def _classify_confirmed(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        event_ids = ", ".join(
            event.event_id
            for event in events
        )

        return ContinuityClassification(
            transition_id=f"SPLIT-BRAIN:{event_ids}",
            event_type=EventType.SPLIT_BRAIN,
            service_continuity=ContinuityStatus.UNVERIFIED,
            runtime_continuity=ContinuityStatus.CONFLICTED,
            execution_continuity=ContinuityStatus.CONFLICTED,
            state_continuity=ContinuityStatus.CONFLICTED,
            authority_continuity=ContinuityStatus.CONFLICTED,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.CONFLICTED,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.SPLIT_BRAIN_DETECTED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.CONFIRMED_SPLIT_BRAIN_RULE,),
            reasons=(
                "Multiple runtimes claim the PRIMARY authority role.",
                "Each PRIMARY runtime has active-authority evidence.",
                "Each PRIMARY runtime has valid lease evidence.",
                "Distinct runtime and execution identities are concurrently active.",
                "State identities diverge under conflicting authority.",
            ),
            missing_evidence=(),
            conflicts=(
                "Multiple active PRIMARY authority holders detected.",
                "Concurrent authority creates split-brain risk.",
                "State and execution outcomes may diverge.",
            ),
        )

    def _classify_unverified(
        self,
        events: tuple[ProcessEvent, ...],
        missing_evidence: tuple[str, ...],
    ) -> ContinuityClassification:
        event_ids = ", ".join(
            event.event_id
            for event in events
        )

        return ContinuityClassification(
            transition_id=f"SPLIT-BRAIN:{event_ids}",
            event_type=EventType.SPLIT_BRAIN,
            service_continuity=ContinuityStatus.UNVERIFIED,
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.UNKNOWN,
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.SPLIT_BRAIN_DETECTED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_SPLIT_BRAIN_RULE,),
            reasons=(
                "Multiple runtimes claim the PRIMARY authority role.",
                "Required active-authority or lease evidence is incomplete.",
                "A confirmed split-brain condition cannot yet be admitted.",
                "Authority topology remains unresolved.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_clear(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        event_ids = ", ".join(
            event.event_id
            for event in events
        )

        return ContinuityClassification(
            transition_id=f"AUTHORITY-CLEAR:{event_ids}",
            event_type=EventType.SPLIT_BRAIN,
            service_continuity=ContinuityStatus.CONTINUOUS,
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
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.SPLIT_BRAIN_DETECTED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.CLEAR_AUTHORITY_RULE,),
            reasons=(
                "Only one runtime holds the PRIMARY authority role.",
                "Other observed runtimes do not claim exclusive authority.",
                "No split-brain authority conflict was detected.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _find_missing_evidence(
        self,
        primary_events: tuple[ProcessEvent, ...],
    ) -> tuple[str, ...]:
        missing: list[str] = []

        for event in primary_events:
            normalized_evidence = tuple(
                evidence_id.upper()
                for evidence_id in event.evidence_ids
            )

            if not any(
                self.PRIMARY_EVIDENCE_HINT in evidence_id
                for evidence_id in normalized_evidence
            ):
                missing.append(
                    f"{event.event_id} active primary evidence"
                )

            if not any(
                self.VALID_LEASE_HINT in evidence_id
                for evidence_id in normalized_evidence
            ):
                missing.append(
                    f"{event.event_id} valid lease evidence"
                )

        return tuple(missing)