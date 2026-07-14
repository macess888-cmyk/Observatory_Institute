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


class FailoverClassificationError(ValueError):
    """Raised when events do not form a valid failover transition."""


class FailoverClassifier:
    """Classifies verified, stale, and unverified failover transitions."""

    VERIFIED_FAILOVER_RULE = "FO-001"
    STALE_FAILOVER_RULE = "FO-002"
    UNVERIFIED_FAILOVER_RULE = "FO-003"

    VERIFIED_EVIDENCE_HINTS = (
        "FAILOVER",
        "AUTHORITY-TRANSFER",
        "STATE-SYNC",
        "SOURCE-DEACTIVATION",
    )

    STALE_EVIDENCE_HINTS = (
        "FAILOVER",
        "AUTHORITY-TRANSFER",
        "STALE-STATE",
        "SOURCE-DEACTIVATION",
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

        self._validate_common_transition(previous, current)

        normalized_evidence = tuple(
            evidence_id.upper()
            for evidence_id in current.evidence_ids
        )

        if self._contains_all(
            normalized_evidence,
            self.VERIFIED_EVIDENCE_HINTS,
        ):
            return self._classify_verified(previous, current)

        if self._contains_all(
            normalized_evidence,
            self.STALE_EVIDENCE_HINTS,
        ):
            return self._classify_stale(previous, current)

        missing_evidence = self._find_missing_failover_evidence(
            normalized_evidence
        )

        return self._classify_unverified(
            previous,
            current,
            missing_evidence,
        )

    def _validate_common_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> None:
        if current.event_type is not EventType.FAILOVER:
            raise FailoverClassificationError(
                "Current event must use EventType.FAILOVER."
            )

        if previous.event_id not in current.parent_event_ids:
            raise FailoverClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise FailoverClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise FailoverClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id == previous.runtime_id:
            raise FailoverClassificationError(
                "Runtime identity must change during failover."
            )

        if current.execution_id == previous.execution_id:
            raise FailoverClassificationError(
                "Execution identity must change during failover."
            )

        if previous.authority_role != "PRIMARY":
            raise FailoverClassificationError(
                "Previous runtime must hold the PRIMARY authority role."
            )

        if current.authority_role != "PRIMARY":
            raise FailoverClassificationError(
                "Failover successor must hold the PRIMARY authority role."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if previous.state_id not in current.parent_state_ids:
            return self._classify_unverified(
                previous,
                current,
                ("parent state evidence",),
            )

        if current.state_id != previous.state_id:
            return self._classify_stale(previous, current)

        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.FAILOVER,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.FAILOVER,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_FAILOVER_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "The previous runtime terminated and a successor runtime "
                "assumed service responsibility.",
                "The previous execution terminated and a successor execution "
                "became active.",
                "Authority transferred to the successor runtime.",
                "State synchronization evidence supports linear continuity.",
                "Availability remained continuous through failover.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _classify_stale(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.FAILOVER,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.DEGRADED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.DISCONTINUOUS,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.FAILOVER,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.STALE_FAILOVER_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "Authority transferred to the successor runtime.",
                "Availability remained continuous through failover.",
                "The successor state differs from the previous primary state.",
                "Stale-state evidence indicates degraded state continuity.",
            ),
            missing_evidence=(),
            conflicts=(
                "The successor may not contain the latest committed state.",
            ),
        )

    def _classify_unverified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
        missing_evidence: tuple[str, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.FAILOVER,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNKNOWN,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.FAILOVER,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_FAILOVER_RULE,),
            reasons=(
                "A failover transition was declared.",
                "The runtime and execution identities changed.",
                "Required failover evidence was incomplete.",
                "Authority, state, and continuity claims cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _find_missing_failover_evidence(
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

    @staticmethod
    def _contains_all(
        evidence: tuple[str, ...],
        required_hints: tuple[str, ...],
    ) -> bool:
        return all(
            any(hint in item for item in evidence)
            for hint in required_hints
        )