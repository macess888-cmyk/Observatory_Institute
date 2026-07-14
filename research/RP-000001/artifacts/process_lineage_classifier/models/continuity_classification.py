from dataclasses import dataclass

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


@dataclass(frozen=True)
class ContinuityClassification:
    """Immutable layered continuity result for prototype version 0.1."""

    transition_id: str
    event_type: EventType

    service_continuity: ContinuityStatus
    runtime_continuity: ContinuityStatus
    execution_continuity: ContinuityStatus
    state_continuity: ContinuityStatus
    authority_continuity: ContinuityStatus
    availability_continuity: ContinuityStatus

    state_lineage: LineageStatus
    binding_status: BindingStatus
    conflict_status: ConflictStatus
    transition_status: TransitionStatus
    operational_status: OperationalStatus
    confidence: ConfidenceLevel

    classifier_version: str = "0.1.0"

    applied_rules: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required_text_fields = {
            "transition_id": self.transition_id,
            "classifier_version": self.classifier_version,
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        enum_fields = {
            "event_type": (self.event_type, EventType),
            "service_continuity": (
                self.service_continuity,
                ContinuityStatus,
            ),
            "runtime_continuity": (
                self.runtime_continuity,
                ContinuityStatus,
            ),
            "execution_continuity": (
                self.execution_continuity,
                ContinuityStatus,
            ),
            "state_continuity": (
                self.state_continuity,
                ContinuityStatus,
            ),
            "authority_continuity": (
                self.authority_continuity,
                ContinuityStatus,
            ),
            "availability_continuity": (
                self.availability_continuity,
                ContinuityStatus,
            ),
            "state_lineage": (self.state_lineage, LineageStatus),
            "binding_status": (self.binding_status, BindingStatus),
            "conflict_status": (self.conflict_status, ConflictStatus),
            "transition_status": (
                self.transition_status,
                TransitionStatus,
            ),
            "operational_status": (
                self.operational_status,
                OperationalStatus,
            ),
            "confidence": (self.confidence, ConfidenceLevel),
        }

        for field_name, (value, expected_type) in enum_fields.items():
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{field_name} must be a {expected_type.__name__}."
                )

        tuple_fields = {
            "applied_rules": self.applied_rules,
            "reasons": self.reasons,
            "missing_evidence": self.missing_evidence,
            "conflicts": self.conflicts,
        }

        for field_name, values in tuple_fields.items():
            if not isinstance(values, tuple):
                raise TypeError(f"{field_name} must be a tuple.")

            if any(
                not isinstance(value, str) or not value.strip()
                for value in values
            ):
                raise ValueError(
                    f"{field_name} must contain only non-empty strings."
                )