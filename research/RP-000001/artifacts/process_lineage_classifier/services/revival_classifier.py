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


class RevivalClassificationError(ValueError):
    """Raised when events do not form a valid revival transition."""


class RevivalClassifier:
    """Classifies verified, unverified, and conflicted revivals."""

    VERIFIED_REVIVAL_RULE = "RV-001"
    UNVERIFIED_REVIVAL_RULE = "RV-002"
    AUTHORITY_CONFLICT_RULE = "RV-003"

    VERIFIED_EVIDENCE_HINTS = (
        "REVIVAL",
        "STATE-RESTORE",
        "AUTHORITY-GRANT",
        "NO-ACTIVE-PRIMARY",
    )

    AUTHORITY_CONFLICT_HINT = "ACTIVE-PRIMARY-CONFLICT"

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
            self.AUTHORITY_CONFLICT_HINT in evidence_id
            for evidence_id in normalized_evidence
        ):
            return self._classify_authority_conflict(previous, current)

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
        if previous.event_type is not EventType.TERMINATE:
            raise RevivalClassificationError(
                "Revival source must be an EventType.TERMINATE event."
            )

        if current.event_type is not EventType.REVIVE:
            raise RevivalClassificationError(
                "Current event must use EventType.REVIVE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise RevivalClassificationError(
                "Current event must reference the terminated event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise RevivalClassificationError(
                "Current event sequence must follow the terminated event."
            )

        if current.service_id != previous.service_id:
            raise RevivalClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id == previous.runtime_id:
            raise RevivalClassificationError(
                "Revival must create a new runtime identity."
            )

        if current.execution_id == previous.execution_id:
            raise RevivalClassificationError(
                "Revival must create a new execution identity."
            )

        if previous.state_id not in current.parent_state_ids:
            raise RevivalClassificationError(
                "Revival must reference the terminated state as a parent."
            )

        if current.state_id != previous.state_id:
            raise RevivalClassificationError(
                "Revival must restore the terminated state identity."
            )

        if not current.snapshot_id:
            raise RevivalClassificationError(
                "Revival requires a snapshot identity."
            )

        if previous.authority_role != "NONE":
            raise RevivalClassificationError(
                "Revival source must have the NONE authority role."
            )

        if current.authority_role != "PRIMARY":
            raise RevivalClassificationError(
                "Revived runtime must hold the PRIMARY authority role."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.REVIVE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.RESTORED,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.REVIVED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_REVIVAL_RULE,),
            reasons=(
                "The service had previously terminated.",
                "A new runtime and execution were created.",
                "The prior state was restored from an explicit snapshot.",
                "Authority was granted to the revived PRIMARY runtime.",
                "Availability was interrupted between termination and revival.",
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
            event_type=EventType.REVIVE,
            service_continuity=ContinuityStatus.UNVERIFIED,
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.REVIVED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_REVIVAL_RULE,),
            reasons=(
                "A revival transition was declared.",
                "A new runtime and execution were created.",
                "Required revival evidence was incomplete.",
                "State restoration and authority admission cannot be established.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )

    def _classify_authority_conflict(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.REVIVE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.RESTORED,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.REVIVED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.AUTHORITY_CONFLICT_RULE,),
            reasons=(
                "The prior state was restored into a new runtime.",
                "Authority was granted to the revived runtime.",
                "Evidence indicates another active PRIMARY authority holder.",
                "Exclusive authority cannot be admitted.",
            ),
            missing_evidence=(),
            conflicts=(
                "Active PRIMARY authority collision detected during revival.",
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