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


class AddressChangeClassificationError(ValueError):
    """Raised when events do not form a valid address-change transition."""


class AddressChangeClassifier:
    """Classifies a valid address-change transition."""

    RULE_ID = "AC-001"

    def classify(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        if not isinstance(previous, ProcessEvent):
            raise TypeError("previous must be a ProcessEvent.")

        if not isinstance(current, ProcessEvent):
            raise TypeError("current must be a ProcessEvent.")

        if current.event_type is not EventType.ADDRESS_CHANGE:
            raise AddressChangeClassificationError(
                "Current event must use EventType.ADDRESS_CHANGE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise AddressChangeClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise AddressChangeClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise AddressChangeClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise AddressChangeClassificationError(
                "Runtime identity must remain unchanged."
            )

        if current.execution_id != previous.execution_id:
            raise AddressChangeClassificationError(
                "Execution identity must remain unchanged."
            )

        if current.state_id != previous.state_id:
            raise AddressChangeClassificationError(
                "State identity must remain unchanged."
            )

        if current.host_id != previous.host_id:
            raise AddressChangeClassificationError(
                "Host identity must remain unchanged."
            )

        if current.authority_role != previous.authority_role:
            raise AddressChangeClassificationError(
                "Authority role must remain unchanged."
            )

        if current.address == previous.address:
            raise AddressChangeClassificationError(
                "Address must change for an address-change transition."
            )

        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.ADDRESS_CHANGE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.ADDRESS_REBOUND,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.RULE_ID,),
            reasons=(
                "The service, runtime, execution, state, host, and authority "
                "identities remained unchanged.",
                f"The address changed from {previous.address} to "
                f"{current.address}.",
                "The current event directly references the previous event.",
            ),
            missing_evidence=(),
            conflicts=(),
        )