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


class AuthorityConvergenceClassificationError(ValueError):
    """Raised when events cannot form a convergence assessment."""


class AuthorityConvergenceClassifier:
    """Classifies verified, incomplete, conflicted, and divergent convergence."""

    VERIFIED_CONVERGENCE_RULE = "ACV-001"
    UNVERIFIED_CONVERGENCE_RULE = "ACV-002"
    AUTHORITY_CONFLICT_RULE = "ACV-003"
    STATE_DIVERGENCE_RULE = "ACV-004"

    AUTHORITY_GRANT_HINT = "AUTHORITY-GRANT"
    AUTHORITY_REVOCATION_HINT = "AUTHORITY-REVOCATION"
    QUORUM_CONFIRMATION_HINT = "QUORUM-CONFIRMATION"
    CONVERGENCE_ACK_HINT = "CONVERGENCE-ACK"
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
            raise AuthorityConvergenceClassificationError(
                "Authority convergence requires at least two events."
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
            primary_event=primary_events[0],
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
            raise AuthorityConvergenceClassificationError(
                "All events must share one service identity."
            )

        event_ids = [
            event.event_id
            for event in events
        ]

        if len(set(event_ids)) != len(event_ids):
            raise AuthorityConvergenceClassificationError(
                "Duplicate event identity detected."
            )

        runtime_ids = [
            event.runtime_id
            for event in events
        ]

        if len(set(runtime_ids)) != len(runtime_ids):
            raise AuthorityConvergenceClassificationError(
                "Duplicate runtime identity detected."
            )

        execution_ids = [
            event.execution_id
            for event in events
        ]

        if len(set(execution_ids)) != len(execution_ids):
            raise AuthorityConvergenceClassificationError(
                "Duplicate execution identity detected."
            )

        sequence_numbers = [
            event.sequence_number
            for event in events
        ]

        if sequence_numbers != sorted(sequence_numbers):
            raise AuthorityConvergenceClassificationError(
                "Event sequence numbers must be increasing."
            )

        if len(set(sequence_numbers)) != len(sequence_numbers):
            raise AuthorityConvergenceClassificationError(
                "Event sequence numbers must be distinct and increasing."
            )

    def _classify_verified(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        transition_id = self._transition_id(events)

        return ContinuityClassification(
            transition_id=transition_id,
            event_type=EventType.AUTHORITY_CONVERGENCE,
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
            state_lineage=LineageStatus.RECONCILED,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.AUTHORITY_CONVERGED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_CONVERGENCE_RULE,),
            reasons=(
                "Authority converged on a single PRIMARY runtime.",
                "Quorum confirmation supports the elected authority holder.",
                "Authority revocation evidence exists for the former PRIMARY.",
                "All observed runtimes acknowledged convergence.",
                "No unresolved authority collision remains.",
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
            event_type=EventType.AUTHORITY_CONVERGENCE,
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
            transition_status=TransitionStatus.AUTHORITY_CONVERGED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_CONVERGENCE_RULE,),
            reasons=(
                "A single PRIMARY runtime is currently declared.",
                "Required convergence evidence is incomplete.",
                "Authority convergence cannot yet be admitted.",
                "Runtime, execution, and state relationships remain unverified.",
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
            event_type=EventType.AUTHORITY_CONVERGENCE,
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
            transition_status=TransitionStatus.AUTHORITY_CONVERGED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.AUTHORITY_CONFLICT_RULE,),
            reasons=(
                "Authority convergence was attempted.",
                "Multiple PRIMARY authority holders remain active.",
                "Exclusive authority has not converged.",
                "Runtime and execution outcomes may continue to diverge.",
            ),
            missing_evidence=(),
            conflicts=(
                "Multiple PRIMARY authority holders remain.",
                "Authority convergence is incomplete.",
            ),
        )

    def _classify_state_divergence(
        self,
        events: tuple[ProcessEvent, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=self._transition_id(events),
            event_type=EventType.AUTHORITY_CONVERGENCE,
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
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.CONFLICTED,
            binding_status=BindingStatus.BOUND,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.AUTHORITY_CONVERGED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.STATE_DIVERGENCE_RULE,),
            reasons=(
                "Authority converged on a single PRIMARY runtime.",
                "Observed state identities remain divergent.",
                "State-divergence evidence prevents lineage reconciliation.",
                "Authority convergence does not establish state convergence.",
            ),
            missing_evidence=(),
            conflicts=(
                "State divergence remains after authority convergence.",
            ),
        )

    def _find_missing_evidence(
        self,
        events: tuple[ProcessEvent, ...],
        *,
        primary_event: ProcessEvent,
    ) -> tuple[str, ...]:
        missing: list[str] = []

        primary_evidence = self._normalized_evidence(primary_event)

        if not self._contains_hint(
            primary_evidence,
            self.AUTHORITY_GRANT_HINT,
        ):
            missing.append("authority grant evidence")

        if not self._contains_hint(
            primary_evidence,
            self.QUORUM_CONFIRMATION_HINT,
        ):
            missing.append("quorum confirmation evidence")

        non_primary_events = tuple(
            event
            for event in events
            if event.event_id != primary_event.event_id
        )

        if not any(
            self._contains_hint(
                self._normalized_evidence(event),
                self.AUTHORITY_REVOCATION_HINT,
            )
            for event in non_primary_events
        ):
            missing.append("authority revocation evidence")

        for event in events:
            if not self._contains_hint(
                self._normalized_evidence(event),
                self.CONVERGENCE_ACK_HINT,
            ):
                missing.append(
                    f"{event.event_id} convergence acknowledgement"
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
        return f"AUTHORITY-CONVERGENCE:{event_ids}"