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


class ResumeClassificationError(ValueError):
    """Raised when events do not form a valid resume transition."""


class ResumeClassifier:
    """Classifies verified, unverified, conflicted, and stale resumes."""

    VERIFIED_RESUME_RULE = "RSU-001"
    UNVERIFIED_RESUME_RULE = "RSU-002"
    AUTHORITY_CONFLICT_RULE = "RSU-003"
    STALE_RESUME_RULE = "RSU-004"

    VERIFIED_EVIDENCE_HINTS = (
        "RESUME",
        "EXECUTION-RESUME",
        "STATE-VERIFY",
        "AUTHORITY-RESTORE",
        "NO-ACTIVE-PRIMARY",
    )

    STALE_EVIDENCE_HINTS = (
        "RESUME",
        "EXECUTION-RESUME",
        "STALE-STATE",
        "AUTHORITY-RESTORE",
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

        if self._contains_all(
            normalized_evidence,
            self.STALE_EVIDENCE_HINTS,
        ):
            return self._classify_stale(previous, current)

        missing_evidence = self._find_missing_evidence(
            normalized_evidence
        )

        if missing_evidence:
            return self._classify_unverified(
                previous,
                current,
                missing_evidence,
            )

        if (
            previous.state_id not in current.parent_state_ids
            or current.state_id != previous.state_id
        ):
            return self._classify_stale(previous, current)

        return self._classify_verified(previous, current)

    def _validate_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> None:
        if previous.event_type is not EventType.PAUSE:
            raise ResumeClassificationError(
                "Resume source must be an EventType.PAUSE event."
            )

        if current.event_type is not EventType.RESUME:
            raise ResumeClassificationError(
                "Current event must use EventType.RESUME."
            )

        if previous.event_id not in current.parent_event_ids:
            raise ResumeClassificationError(
                "Current event must reference the paused event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise ResumeClassificationError(
                "Current event sequence must follow the paused event."
            )

        if current.service_id != previous.service_id:
            raise ResumeClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise ResumeClassificationError(
                "Runtime identity must remain unchanged during resume."
            )

        if current.execution_id != previous.execution_id:
            raise ResumeClassificationError(
                "Execution identity must remain unchanged during resume."
            )

        if current.host_id != previous.host_id:
            raise ResumeClassificationError(
                "Host identity must remain unchanged during resume."
            )

        if current.address != previous.address:
            raise ResumeClassificationError(
                "Address must remain unchanged during resume."
            )

        if previous.authority_role != "NONE":
            raise ResumeClassificationError(
                "Paused source must use the NONE authority role."
            )

        if current.authority_role != "PRIMARY":
            raise ResumeClassificationError(
                "Resumed runtime must hold the PRIMARY authority role."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.RESUME,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.RESUMED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_RESUME_RULE,),
            reasons=(
                "The process resumed from a paused state.",
                "The runtime and execution identities remained unchanged.",
                "State verification supports linear state continuity.",
                "Authority was restored to the resumed PRIMARY runtime.",
                "Availability was interrupted during the pause interval.",
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
            event_type=EventType.RESUME,
            service_continuity=ContinuityStatus.UNVERIFIED,
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.UNVERIFIED,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.RESUMED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_RESUME_RULE,),
            reasons=(
                "A resume transition was declared.",
                "The runtime identity remained unchanged.",
                "Required resume evidence was incomplete.",
                "Execution, state, and authority restoration cannot be admitted.",
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
            event_type=EventType.RESUME,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.UNVERIFIED,
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.COLLIDING,
            conflict_status=ConflictStatus.COLLIDING,
            transition_status=TransitionStatus.RESUMED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.AUTHORITY_CONFLICT_RULE,),
            reasons=(
                "The paused execution resumed.",
                "The runtime and state identities remained stable.",
                "Evidence indicates another active PRIMARY authority holder.",
                "Exclusive authority cannot be restored.",
            ),
            missing_evidence=(),
            conflicts=(
                "Active PRIMARY authority collision detected during resume.",
            ),
        )

    def _classify_stale(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.RESUME,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.CONTINUOUS,
            execution_continuity=ContinuityStatus.CONTINUOUS,
            state_continuity=ContinuityStatus.DEGRADED,
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=ContinuityStatus.INTERRUPTED,
            state_lineage=LineageStatus.DISCONTINUOUS,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CONFLICTED,
            transition_status=TransitionStatus.RESUMED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.STALE_RESUME_RULE,),
            reasons=(
                "The paused execution resumed.",
                "The runtime and execution identities remained stable.",
                "The resumed state differs from the paused state.",
                "Stale-state evidence indicates degraded continuity.",
            ),
            missing_evidence=(),
            conflicts=(
                "The resumed state may not contain the latest preserved state.",
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

    @staticmethod
    def _contains_all(
        evidence: tuple[str, ...],
        required_hints: tuple[str, ...],
    ) -> bool:
        return all(
            any(hint in item for item in evidence)
            for hint in required_hints
        )