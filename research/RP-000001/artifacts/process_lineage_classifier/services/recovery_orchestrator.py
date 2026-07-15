from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)
from models import (
    ContinuityClassification,
    RecoveryDecision,
)


class RecoveryOrchestrationError(ValueError):
    """Raised when recovery assessments cannot be orchestrated."""


class RecoveryOrchestrator:
    """Produces observer-only recovery decisions from existing assessments."""

    RECOVERY_READY_RULE = "RO-001"
    RECOVERY_HOLD_RULE = "RO-002"
    MISSING_ASSESSMENT_RULE = "RO-003"

    REQUIRED_EVENT_TYPES = (
        EventType.AUTHORITY_CONVERGENCE,
        EventType.LINEAGE_RECONCILIATION,
        EventType.ROLLBACK_RECOVERY,
    )

    def orchestrate(
        self,
        assessments: tuple[ContinuityClassification, ...],
    ) -> RecoveryDecision:
        if not isinstance(assessments, tuple):
            raise TypeError("assessments must be a tuple.")

        if any(
            not isinstance(
                assessment,
                ContinuityClassification,
            )
            for assessment in assessments
        ):
            raise TypeError(
                "assessments must contain only "
                "ContinuityClassification instances."
            )

        if not assessments:
            raise RecoveryOrchestrationError(
                "Recovery orchestration requires at least one assessment."
            )

        self._validate_assessment_types(assessments)

        assessment_by_type = {
            assessment.event_type: assessment
            for assessment in assessments
        }

        missing_types = tuple(
            event_type
            for event_type in self.REQUIRED_EVENT_TYPES
            if event_type not in assessment_by_type
        )

        passed_assessments = sum(
            assessment.operational_status
            is OperationalStatus.PASS
            for assessment in assessments
        )

        held_assessments = sum(
            assessment.operational_status
            is OperationalStatus.HOLD
            for assessment in assessments
        )

        if missing_types:
            return self._missing_assessment_decision(
                assessments,
                missing_types=missing_types,
                passed_assessments=passed_assessments,
                held_assessments=held_assessments,
            )

        if any(
            assessment.operational_status
            is not OperationalStatus.PASS
            for assessment in assessments
        ):
            return self._hold_decision(
                assessments,
                passed_assessments=passed_assessments,
                held_assessments=held_assessments,
            )

        return self._ready_decision()

    def _validate_assessment_types(
        self,
        assessments: tuple[ContinuityClassification, ...],
    ) -> None:
        event_types = [
            assessment.event_type
            for assessment in assessments
        ]

        unexpected_types = tuple(
            event_type
            for event_type in event_types
            if event_type not in self.REQUIRED_EVENT_TYPES
        )

        if unexpected_types:
            raise RecoveryOrchestrationError(
                "Recovery orchestration received an unexpected "
                "assessment type."
            )

        if len(set(event_types)) != len(event_types):
            raise RecoveryOrchestrationError(
                "Recovery orchestration received a duplicate "
                "assessment type."
            )

    def _ready_decision(self) -> RecoveryDecision:
        return RecoveryDecision(
            status=RecoveryDecisionStatus.RECOVERY_READY,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            required_assessments=len(self.REQUIRED_EVENT_TYPES),
            passed_assessments=len(self.REQUIRED_EVENT_TYPES),
            held_assessments=0,
            missing_assessment_types=(),
            applied_rules=(self.RECOVERY_READY_RULE,),
            reasons=(
                "Authority convergence assessment passed.",
                "Lineage reconciliation assessment passed.",
                "Rollback recovery integrity assessment passed.",
                "The recovery decision remains observer-only.",
            ),
            missing_evidence=(),
            conflicts=(),
            execution_requested=False,
            side_effects_permitted=False,
        )

    def _hold_decision(
        self,
        assessments: tuple[ContinuityClassification, ...],
        *,
        passed_assessments: int,
        held_assessments: int,
    ) -> RecoveryDecision:
        missing_evidence = self._collect_unique_strings(
            assessment.missing_evidence
            for assessment in assessments
        )
        conflicts = self._collect_unique_strings(
            assessment.conflicts
            for assessment in assessments
        )

        confidence = self._lowest_confidence(assessments)

        return RecoveryDecision(
            status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=confidence,
            required_assessments=len(self.REQUIRED_EVENT_TYPES),
            passed_assessments=passed_assessments,
            held_assessments=held_assessments,
            missing_assessment_types=(),
            applied_rules=(self.RECOVERY_HOLD_RULE,),
            reasons=(
                "One or more required recovery assessments remain held.",
                "Recovery readiness cannot be admitted.",
                "Missing evidence and conflicts were preserved.",
                "The recovery decision remains observer-only.",
            ),
            missing_evidence=missing_evidence,
            conflicts=conflicts,
            execution_requested=False,
            side_effects_permitted=False,
        )

    def _missing_assessment_decision(
        self,
        assessments: tuple[ContinuityClassification, ...],
        *,
        missing_types: tuple[EventType, ...],
        passed_assessments: int,
        held_assessments: int,
    ) -> RecoveryDecision:
        missing_evidence = tuple(
            f"{event_type.value} assessment"
            for event_type in missing_types
        )

        return RecoveryDecision(
            status=RecoveryDecisionStatus.RECOVERY_HOLD,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            required_assessments=len(self.REQUIRED_EVENT_TYPES),
            passed_assessments=passed_assessments,
            held_assessments=held_assessments,
            missing_assessment_types=missing_types,
            applied_rules=(self.MISSING_ASSESSMENT_RULE,),
            reasons=(
                "One or more required recovery assessments are missing.",
                "Recovery readiness cannot be evaluated completely.",
                "No execution or mutation was requested.",
                "The recovery decision remains observer-only.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _collect_unique_strings(
        groups: object,
    ) -> tuple[str, ...]:
        collected: list[str] = []

        for group in groups:
            for value in group:
                if value not in collected:
                    collected.append(value)

        return tuple(collected)

    @staticmethod
    def _lowest_confidence(
        assessments: tuple[ContinuityClassification, ...],
    ) -> ConfidenceLevel:
        confidence_order = {
            ConfidenceLevel.LOW: 0,
            ConfidenceLevel.MODERATE: 1,
            ConfidenceLevel.HIGH: 2,
        }

        return min(
            (
                assessment.confidence
                for assessment in assessments
            ),
            key=confidence_order.__getitem__,
        )