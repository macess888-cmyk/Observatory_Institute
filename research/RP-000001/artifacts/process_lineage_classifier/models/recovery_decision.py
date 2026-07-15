from dataclasses import dataclass

from enums import (
    ConfidenceLevel,
    EventType,
    OperationalStatus,
    RecoveryDecisionStatus,
)


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """Immutable observer-only recovery orchestration result."""

    status: RecoveryDecisionStatus
    operational_status: OperationalStatus
    confidence: ConfidenceLevel
    required_assessments: int
    passed_assessments: int
    held_assessments: int
    missing_assessment_types: tuple[EventType, ...]
    applied_rules: tuple[str, ...]
    reasons: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    conflicts: tuple[str, ...]
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.status, RecoveryDecisionStatus):
            raise TypeError(
                "status must be a RecoveryDecisionStatus."
            )

        if not isinstance(
            self.operational_status,
            OperationalStatus,
        ):
            raise TypeError(
                "operational_status must be an OperationalStatus."
            )

        if not isinstance(self.confidence, ConfidenceLevel):
            raise TypeError(
                "confidence must be a ConfidenceLevel."
            )

        for field_name, value in (
            ("required_assessments", self.required_assessments),
            ("passed_assessments", self.passed_assessments),
            ("held_assessments", self.held_assessments),
        ):
            if not isinstance(value, int):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

            if value < 0:
                raise ValueError(
                    f"{field_name} must not be negative."
                )

        if (
            self.passed_assessments + self.held_assessments
            > self.required_assessments
        ):
            raise ValueError(
                "Passed and held assessments cannot exceed "
                "required assessments."
            )

        self._require_tuple(
            self.missing_assessment_types,
            "missing_assessment_types",
        )
        self._require_tuple(
            self.applied_rules,
            "applied_rules",
        )
        self._require_tuple(self.reasons, "reasons")
        self._require_tuple(
            self.missing_evidence,
            "missing_evidence",
        )
        self._require_tuple(self.conflicts, "conflicts")

        if any(
            not isinstance(event_type, EventType)
            for event_type in self.missing_assessment_types
        ):
            raise TypeError(
                "missing_assessment_types must contain "
                "only EventType values."
            )

        for field_name, values in (
            ("applied_rules", self.applied_rules),
            ("reasons", self.reasons),
            ("missing_evidence", self.missing_evidence),
            ("conflicts", self.conflicts),
        ):
            if any(
                not isinstance(value, str)
                for value in values
            ):
                raise TypeError(
                    f"{field_name} must contain only strings."
                )

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryDecision must remain observer-only; "
                "execution_requested must be False."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryDecision must not permit side effects."
            )

    @staticmethod
    def _require_tuple(
        value: tuple[object, ...],
        field_name: str,
    ) -> None:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field_name} must be a tuple."
            )