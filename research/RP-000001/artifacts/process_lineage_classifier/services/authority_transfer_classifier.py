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


class AuthorityTransferClassificationError(ValueError):
    """Raised when events do not form a valid authority transfer."""


class AuthorityTransferClassifier:
    """Classifies verified, stale, and unverified authority transfers."""

    VERIFIED_TRANSFER_RULE = "AT-001"
    UNVERIFIED_TRANSFER_RULE = "AT-002"
    STALE_TRANSFER_RULE = "AT-003"

    VERIFIED_EVIDENCE_HINTS = (
        "AUTHORITY-TRANSFER",
        "SOURCE-DEMOTION",
        "TARGET-PROMOTION",
        "STATE-SYNC",
    )

    STALE_EVIDENCE_HINTS = (
        "AUTHORITY-TRANSFER",
        "SOURCE-DEMOTION",
        "TARGET-PROMOTION",
        "STALE-STATE",
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
            if (
                previous.state_id in current.parent_state_ids
                and current.state_id == previous.state_id
            ):
                return self._classify_verified(previous, current)

        if self._contains_all(
            normalized_evidence,
            self.STALE_EVIDENCE_HINTS,
        ):
            return self._classify_stale(previous, current)

        missing_evidence = self._find_missing_evidence(
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
        if current.event_type is not EventType.AUTHORITY_TRANSFER:
            raise AuthorityTransferClassificationError(
                "Current event must use EventType.AUTHORITY_TRANSFER."
            )

        if previous.event_id not in current.parent_event_ids:
            raise AuthorityTransferClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise AuthorityTransferClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise AuthorityTransferClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id == previous.runtime_id:
            raise AuthorityTransferClassificationError(
                "Runtime identity must change during authority transfer."
            )

        if current.execution_id == previous.execution_id:
            raise AuthorityTransferClassificationError(
                "Execution identity must change during authority transfer."
            )

        if previous.authority_role != "PRIMARY":
            raise AuthorityTransferClassificationError(
                "Previous runtime must hold the PRIMARY authority role."
            )

        if current.authority_role != "PRIMARY":
            raise AuthorityTransferClassificationError(
                "Authority-transfer successor must hold the PRIMARY role."
            )

    def _classify_verified(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.AUTHORITY_TRANSFER,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.AUTHORITY_TRANSFERRED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_TRANSFER_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "Authority transferred from the previous runtime.",
                "Source demotion evidence was supplied.",
                "Target promotion evidence was supplied.",
                "The runtime and execution identities changed.",
                "State synchronization evidence supports linear continuity.",
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
            event_type=EventType.AUTHORITY_TRANSFER,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=ContinuityStatus.TERMINATED,
            execution_continuity=ContinuityStatus.TERMINATED,
            state_continuity=ContinuityStatus.DEGRADED,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=ContinuityStatus.CONTINUOUS,
            state_lineage=LineageStatus.DISCONTINUOUS,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.AUTHORITY_TRANSFERRED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.MODERATE,
            applied_rules=(self.STALE_TRANSFER_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "Authority transferred from the previous runtime.",
                "Source demotion and target promotion evidence were supplied.",
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
            event_type=EventType.AUTHORITY_TRANSFER,
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
            transition_status=TransitionStatus.AUTHORITY_TRANSFERRED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_TRANSFER_RULE,),
            reasons=(
                "An authority transfer was declared.",
                "The runtime and execution identities changed.",
                "Required authority-transfer evidence was incomplete.",
                "Authority and continuity claims cannot be admitted.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
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