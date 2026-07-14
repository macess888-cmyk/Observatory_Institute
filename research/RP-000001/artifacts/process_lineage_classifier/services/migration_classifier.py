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


class MigrationClassificationError(ValueError):
    """Raised when events do not form a valid migration transition."""


class MigrationClassifier:
    """Classifies verified and unverified migration transitions."""

    VERIFIED_MIGRATION_RULE = "MG-001"
    UNVERIFIED_MIGRATION_RULE = "MG-002"

    REQUIRED_EVIDENCE_HINTS = (
        "MIGRATION",
        "STATE-TRANSFER",
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

        missing_evidence = self._find_missing_evidence(current)

        if missing_evidence:
            return self._classify_unverified_migration(
                previous,
                current,
                missing_evidence,
            )

        return self._classify_verified_migration(previous, current)

    def _validate_common_transition(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> None:
        if current.event_type is not EventType.MIGRATE:
            raise MigrationClassificationError(
                "Current event must use EventType.MIGRATE."
            )

        if previous.event_id not in current.parent_event_ids:
            raise MigrationClassificationError(
                "Current event must reference the previous event as a parent."
            )

        if current.sequence_number <= previous.sequence_number:
            raise MigrationClassificationError(
                "Current event sequence must follow the previous event."
            )

        if current.service_id != previous.service_id:
            raise MigrationClassificationError(
                "Service identity must remain unchanged."
            )

        if current.runtime_id != previous.runtime_id:
            raise MigrationClassificationError(
                "Runtime identity must remain unchanged during migration."
            )

        if current.execution_id != previous.execution_id:
            raise MigrationClassificationError(
                "Execution identity must remain unchanged during migration."
            )

        if current.state_id != previous.state_id:
            raise MigrationClassificationError(
                "State identity must remain unchanged during migration."
            )

        if current.authority_role != previous.authority_role:
            raise MigrationClassificationError(
                "Authority role must remain unchanged during migration."
            )

        if current.host_id == previous.host_id:
            raise MigrationClassificationError(
                "Host identity must change during migration."
            )

        if not current.migration_id:
            raise MigrationClassificationError(
                "Migration transition requires a migration identifier."
            )

    def _find_missing_evidence(
        self,
        current: ProcessEvent,
    ) -> tuple[str, ...]:
        missing: list[str] = []

        if not current.parent_state_ids:
            missing.append("parent state evidence")

        elif current.state_id not in current.parent_state_ids:
            missing.append("current state lineage reference")

        normalized_evidence = tuple(
            evidence_id.upper()
            for evidence_id in current.evidence_ids
        )

        for required_hint in self.REQUIRED_EVIDENCE_HINTS:
            if not any(
                required_hint in evidence_id
                for evidence_id in normalized_evidence
            ):
                missing.append(
                    required_hint.lower().replace("-", " ") + " evidence"
                )

        return tuple(missing)

    def _classify_verified_migration(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.MIGRATE,
            service_continuity=ContinuityStatus.CONTINUOUS,
            runtime_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            execution_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_continuity=ContinuityStatus.CONTINUOUS,
            authority_continuity=ContinuityStatus.CONTINUOUS,
            availability_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            state_lineage=LineageStatus.LINEAR,
            binding_status=BindingStatus.REBOUND,
            conflict_status=ConflictStatus.CLEAR,
            transition_status=TransitionStatus.MIGRATED,
            operational_status=OperationalStatus.PASS,
            confidence=ConfidenceLevel.HIGH,
            applied_rules=(self.VERIFIED_MIGRATION_RULE,),
            reasons=(
                "The logical service identity remained unchanged.",
                "The runtime and execution identities remained stable.",
                f"The runtime migrated from host {previous.host_id} "
                f"to host {current.host_id}.",
                "Migration, state-transfer, and source-deactivation "
                "evidence were supplied.",
                "The state lineage remained linear through migration.",
            ),
            missing_evidence=(),
            conflicts=(),
        )

    def _classify_unverified_migration(
        self,
        previous: ProcessEvent,
        current: ProcessEvent,
        missing_evidence: tuple[str, ...],
    ) -> ContinuityClassification:
        return ContinuityClassification(
            transition_id=f"{previous.event_id}->{current.event_id}",
            event_type=EventType.MIGRATE,
            service_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            runtime_continuity=ContinuityStatus.UNVERIFIED,
            execution_continuity=ContinuityStatus.UNKNOWN,
            state_continuity=ContinuityStatus.UNVERIFIED,
            authority_continuity=(
                ContinuityStatus.CONDITIONALLY_CONTINUOUS
            ),
            availability_continuity=ContinuityStatus.UNKNOWN,
            state_lineage=LineageStatus.UNVERIFIED,
            binding_status=BindingStatus.UNVERIFIED,
            conflict_status=ConflictStatus.UNKNOWN,
            transition_status=TransitionStatus.MIGRATED,
            operational_status=OperationalStatus.HOLD,
            confidence=ConfidenceLevel.LOW,
            applied_rules=(self.UNVERIFIED_MIGRATION_RULE,),
            reasons=(
                f"A migration from host {previous.host_id} "
                f"to host {current.host_id} was declared.",
                "Required migration evidence was incomplete.",
                "Continuity cannot be admitted without a complete "
                "migration bridge.",
            ),
            missing_evidence=missing_evidence,
            conflicts=(),
        )