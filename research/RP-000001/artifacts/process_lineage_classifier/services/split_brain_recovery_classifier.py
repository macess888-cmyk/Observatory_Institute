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


class SplitBrainRecoveryClassificationError(ValueError):
    """Raised when events cannot form a split-brain recovery assessment."""


class SplitBrainRecoveryClassifier:
    """Classifies verified, incomplete, conflicted, and divergent recovery."""

    VERIFIED_RECOVERY_RULE = "SBR-001"
    UNVERIFIED_RECOVERY_RULE = "SBR-002"
    AUTHORITY_CONFLICT_RULE = "SBR-003"
    STATE_DIVERGENCE_RULE = "SBR-004"

    AUTHORITY_GRANT_HINT = "AUTHORITY-GRANT"
    AUTHORITY_REVOCATION_HINT = "AUTHORITY-REVOCATION"
    RUNTIME_ISOLATION_HINT = "RUNTIME-ISOLATION"
    QUORUM_CONFIRMATION_HINT = "QUORUM-CONFIRMATION"
    STATE_RECONCILIATION_HINT = "STATE-RECONCILIATION"
    RECOVERY_ACK_HINT = "RECOVERY-ACK"
    STATE_DIVERGENCE_HINT = "STATE-DIVERGENCE"

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

        if len(events) < 2:
            raise SplitBrainRecoveryClassificationError(
                "Split-brain recovery requires at least two events."
            )

        self._validate_events(events)

        primary_events = tuple(
            event
            for event in events
            if event.authority_role == "PRIMARY"
        )

        if len(primary_events) != 1:
            return self._classify_authority_conflict(events)

        if self._has_state_divergence(events):
            return self._classify_state_divergence(events)

        missing_evidence = self._find_missing_evidence(
            events,
            recovered_primary=primary_events[0],
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
            raise SplitBrainRecoveryClassificationError(
                "All events must share one service identity."
            )

        event_ids = [
            event.event_id
            for event in events
        ]

        if len(set(event_ids)) != len(event_ids):
            raise SplitBrainRecoveryClassificationError(
                "Duplicate event identity detected."
            )

        runtime_ids = [
            event.runtime_id
            for event in events
        ]

        if len(set(runtime_ids)) != len(runtime_ids):
            raise SplitBrainRecoveryClassificationError(
                "Duplicate runtime identity detected."
            )

        execution_ids = [
            event.execution_id
            for event in events
        ]

        if len(set(execution_ids)) != len(execution_ids):
            raise SplitBrainRecoveryClassificationError(
                "Duplicate execution identity detected."
            )

        sequence_numbers = [
            event.sequence_number
            for event in events
        ]

        if sequence_numbers != sorted(sequence_numbers):
            raise SplitBrainRecoveryClassificationError(
                "Event sequence numbers must be increasing."
            )

        if len(set(sequence_numbers)) != len(sequence_numbers):
            raise SplitBrainRecoveryClassificationError(
                "Event sequence numbers must be distinct and increasing."
            )

    def _classify_verified(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.SPLIT_BRAIN_RECOVERY,
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
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.RECONCILED,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.SPLIT_BRAIN_RECOVERED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_RECOVERY_RULE,),
            reasons=(
                "Split-brain recovery converged on a single PRIMARY runtime.",
                "The former PRIMARY was isolated and its authority revoked.",
                "Quorum evidence supports the recovered authority holder.",
                "Divergent state was reconciled to the recovered state.",
                "All observed runtimes acknowledged recovery.",
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
            event_type=EventType.SPLIT_BRAIN_RECOVERY,
            service_continuity=ContinuityStatus.UNVERIFIED,
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
            transition_status=TransitionStatus.SPLIT_BRAIN_RECOVERED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_RECOVERY_RULE,),
            reasons=(
                "A single PRIMARY runtime is currently declared.",
                "Required split-brain recovery evidence is incomplete.",
                "Authority recovery and state reconciliation cannot be admitted.",
                "Runtime and execution relationships remain unverified.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_authority_conflict(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.SPLIT_BRAIN_RECOVERY,
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
            transition_status=TransitionStatus.SPLIT_BRAIN_RECOVERED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.AUTHORITY_CONFLICT_RULE,),
            reasons=(
                "Split-brain recovery was attempted.",
                "Multiple PRIMARY authority holders remain active.",
                "The former authority holder has not been fully isolated.",
                "Authority and state outcomes may continue to diverge.",
            ),
            missing_evidence=(),
            conflicts=(
                "Multiple PRIMARY authority holders remain.",
                "Split-brain recovery is incomplete.",
            ),
        )

    def _classify_state_divergence(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.SPLIT_BRAIN_RECOVERY,
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
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.SPLIT_BRAIN_RECOVERED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.STATE_DIVERGENCE_RULE,),
            reasons=(
                "Authority converged on a single PRIMARY runtime.",
                "The former PRIMARY was isolated.",
                "Observed state identities remain divergent.",
                "State reconciliation has not completed.",
            ),
            missing_evidence=(),
            conflicts=(
                "State divergence remains after authority recovery.",
            ),
        )

    def _find_missing_evidence(
        self,
        events: tuple[ProcessEvent, ...],
        *,
        recovered_primary: ProcessEvent,
    ) -> tuple[str, ...]:
        missing: list[str] = []

        primary_evidence = self._normalized_evidence(
            recovered_primary
        )

        for hint, description in (
            (
                self.AUTHORITY_GRANT_HINT,
                "authority grant evidence",
            ),
            (
                self.QUORUM_CONFIRMATION_HINT,
                "quorum confirmation evidence",
            ),
            (
                self.STATE_RECONCILIATION_HINT,
                "state reconciliation evidence",
            ),
        ):
            if not self._contains_hint(primary_evidence, hint):
                missing.append(description)

        non_primary_events = tuple(
            event
            for event in events
            if event.event_id != recovered_primary.event_id
        )

        if not any(
            self._contains_hint(
                self._normalized_evidence(event),
                self.AUTHORITY_REVOCATION_HINT,
            )
            for event in non_primary_events
        ):
            missing.append("authority revocation evidence")

        if not any(
            self._contains_hint(
                self._normalized_evidence(event),
                self.RUNTIME_ISOLATION_HINT,
            )
            for event in non_primary_events
        ):
            missing.append("runtime isolation evidence")

        for event in events:
            if not self._contains_hint(
                self._normalized_evidence(event),
                self.RECOVERY_ACK_HINT,
            ):
                missing.append(
                    f"{event.event_id} recovery acknowledgement"
                )

        return tuple(missing)

    def _has_state_divergence(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> bool:
        return any(
            self._contains_hint(
                self._normalized_evidence(event),
                self.STATE_DIVERGENCE_HINT,
            )
            for event in events
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
        return f"SPLIT-BRAIN-RECOVERY:{event_ids}"