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


class PromotionClassificationError(ValueError):
    """Raised when events do not form a valid promotion transition."""


class PromotionClassifier:
    """Classifies verified, unverified, and conflicted promotions."""

    VERIFIED_PROMOTION_RULE = "PR-001"
    UNVERIFIED_PROMOTION_RULE = "PR-002"
    CONFLICTED_PROMOTION_RULE = "PR-003"

    VERIFIED_EVIDENCE_HINTS = (
        "PROMOTION",
        "AUTHORITY-GRANT",
        "NO-ACTIVE-PRIMARY",
    )

    CONFLICT_EVIDENCE_HINT = "ACTIVE-PRIMARY-CONFLICT"

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
            self.CONFLICT_EVIDENCE_HINT in evidence_id
            for evidence_id in normalized_evidence
        ):
            return self._classify_conflicted(previous, current)

        missing_evidence = self._find_missing_evidence(
            normalized_evidence
        )

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
        if current.event_type is not EventType.PROMOTE:
            raise PromotionClassificationError(
                "Current event must use EventType.PROMOTE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise PromotionClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise PromotionClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise PromotionClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise PromotionClassificationError(
                "Runtime identity must remain unchanged during promotion."
            )

        if current.execution_id != previous.execution_id:
            raise PromotionClassificationError(
                "Execution identity must remain unchanged during promotion."
            )

        if current.state_id != previous.state_id:
            raise PromotionClassificationError(
                "State identity must remain unchanged during promotion."
            )

        if current.host_id != previous.host_id:
            raise PromotionClassificationError(
                "Host identity must remain unchanged during promotion."
            )

        if current.address != previous.address:
            raise PromotionClassificationError(
                "Address must remain unchanged during promotion."
            )

        if previous.authority_role != "SECONDARY":
            raise PromotionClassificationError(
                "Promotion source must hold the SECONDARY authority role."
            )

        if current.authority_role != "PRIMARY":
            raise PromotionClassificationError(
                "Promotion target must hold the PRIMARY authority role."
            )

        if previous.state_id not in current.parent_state_ids:
            raise PromotionClassificationError(
                "Promotion must reference the previous state as a parent."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.PROMOTE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.PROMOTED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_PROMOTION_RULE,),
            reasons=(
                "The runtime remained continuous through promotion.",
                "The execution and state identities remained unchanged.",
                "The authority role changed from SECONDARY to PRIMARY.",
                "Authority-grant evidence supports the promotion.",
                "Evidence confirms that no other active PRIMARY exists.",
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
            event_type=EventType.PROMOTE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.PROMOTED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_PROMOTION_RULE,),
            reasons=(
                "A promotion from SECONDARY to PRIMARY was declared.",
                "Runtime, execution, and state identities remained stable.",
                "Required promotion evidence was incomplete.",
                "Authority admission cannot be established.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_conflicted(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.PROMOTE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.PROMOTED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.CONFLICTED_PROMOTION_RULE,),
            reasons=(
                "A promotion from SECONDARY to PRIMARY was declared.",
                "Runtime, execution, and state identities remained stable.",
                "Evidence indicates another active PRIMARY authority holder.",
                "Exclusive authority cannot be admitted while the collision remains.",
            ),
            missing_evidence=(),
            conflicts=(
                "Active PRIMARY authority collision detected.",
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