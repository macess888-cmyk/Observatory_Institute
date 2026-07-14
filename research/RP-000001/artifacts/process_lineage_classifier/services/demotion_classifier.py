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


class DemotionClassificationError(ValueError):
    """Raised when events do not form a valid demotion transition."""


class DemotionClassifier:
    """Classifies verified, unverified, and successorless demotions."""

    VERIFIED_DEMOTION_RULE = "DM-001"
    UNVERIFIED_DEMOTION_RULE = "DM-002"
    NO_SUCCESSOR_RULE = "DM-003"

    VERIFIED_EVIDENCE_HINTS = (
        "DEMOTION",
        "AUTHORITY-REVOCATION",
        "SUCCESSOR-PRIMARY",
    )

    NO_SUCCESSOR_EVIDENCE_HINT = "NO-SUCCESSOR-PRIMARY"

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
            self.NO_SUCCESSOR_EVIDENCE_HINT in evidence_id
            for evidence_id in normalized_evidence
        ):
            return self._classify_without_successor(previous, current)

        missing_evidence = self._find_missing_evidence(normalized_evidence)

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
        if current.event_type is not EventType.DEMOTE:
            raise DemotionClassificationError(
                "Current event must use EventType.DEMOTE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise DemotionClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise DemotionClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise DemotionClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise DemotionClassificationError(
                "Runtime identity must remain unchanged during demotion."
            )

        if current.execution_id != previous.execution_id:
            raise DemotionClassificationError(
                "Execution identity must remain unchanged during demotion."
            )

        if current.state_id != previous.state_id:
            raise DemotionClassificationError(
                "State identity must remain unchanged during demotion."
            )

        if current.host_id != previous.host_id:
            raise DemotionClassificationError(
                "Host identity must remain unchanged during demotion."
            )

        if current.address != previous.address:
            raise DemotionClassificationError(
                "Address must remain unchanged during demotion."
            )

        if previous.authority_role != "PRIMARY":
            raise DemotionClassificationError(
                "Demotion source must hold the PRIMARY authority role."
            )

        if current.authority_role != "SECONDARY":
            raise DemotionClassificationError(
                "Demotion target must hold the SECONDARY authority role."
            )

        if previous.state_id not in current.parent_state_ids:
            raise DemotionClassificationError(
                "Demotion must reference the previous state as a parent."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.DEMOTE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.DEMOTED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_DEMOTION_RULE,),
            reasons=(
                "The runtime remained continuous through demotion.",
                "The execution and state identities remained unchanged.",
                "The authority role changed from PRIMARY to SECONDARY.",
                "Authority revocation evidence supports the demotion.",
                "Evidence confirms that a successor PRIMARY exists.",
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
            event_type=EventType.DEMOTE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.DEMOTED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_DEMOTION_RULE,),
            reasons=(
                "A demotion from PRIMARY to SECONDARY was declared.",
                "Runtime, execution, and state identities remained stable.",
                "Required demotion evidence was incomplete.",
                "Authority succession cannot be established.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_without_successor(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.DEMOTE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.INTERRUPTED,
            availability_continuity=ContinuityStatus.DEGRADED,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.EXPIRED,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.DEMOTED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.NO_SUCCESSOR_RULE,),
            reasons=(
                "The authority role changed from PRIMARY to SECONDARY.",
                "Authority revocation evidence supports the demotion.",
                "No successor PRIMARY authority holder was established.",
                "Service authority continuity is interrupted.",
                "Availability may be degraded without an active PRIMARY.",
            ),
            missing_evidence=(),
            conflicts=(
                "No successor PRIMARY authority holder is available.",
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