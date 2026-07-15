from models import RecoveryAuditTrail


class AuditChainIntegrityError(ValueError):
    """Raised when a recovery audit chain fails integrity validation."""


class AuditChainIntegrityValidator:
    """Validates semantic and structural integrity across an audit chain."""

    RECEIPT_EVENT_TYPE = "RECONCILIATION_RECEIPT_ISSUED"

    def validate(
        self,
        trail: RecoveryAuditTrail,
    ) -> bool:
        if not isinstance(trail, RecoveryAuditTrail):
            raise TypeError(
                "trail must be a RecoveryAuditTrail."
            )

        self._validate_contiguous_sequence(trail)
        self._validate_unique_evidence(trail)
        self._validate_receipt_relationships(trail)
        self._validate_actor_consistency(trail)
        self._validate_status_progression(trail)

        return True

    @staticmethod
    def _validate_contiguous_sequence(
        trail: RecoveryAuditTrail,
    ) -> None:
        sequence_numbers = tuple(
            event.sequence_number
            for event in trail.events
        )

        if sequence_numbers[0] != 1:
            raise AuditChainIntegrityError(
                "Audit chain sequence must start at one."
            )

        expected = tuple(
            range(1, len(sequence_numbers) + 1)
        )

        if sequence_numbers != expected:
            raise AuditChainIntegrityError(
                "Audit chain sequence must remain contiguous."
            )

    @staticmethod
    def _validate_unique_evidence(
        trail: RecoveryAuditTrail,
    ) -> None:
        evidence_ids = tuple(
            evidence_id
            for event in trail.events
            for evidence_id in event.evidence_ids
        )

        if len(set(evidence_ids)) != len(evidence_ids):
            raise AuditChainIntegrityError(
                "duplicate evidence identity detected across audit chain."
            )

    def _validate_receipt_relationships(
        self,
        trail: RecoveryAuditTrail,
    ) -> None:
        receipt_events = tuple(
            event
            for event in trail.events
            if event.event_type == self.RECEIPT_EVENT_TYPE
        )

        for event in trail.events:
            if event.event_type == self.RECEIPT_EVENT_TYPE:
                if event.related_receipt_id is None:
                    raise AuditChainIntegrityError(
                        "Receipt event requires a receipt identity."
                    )
            elif event.related_receipt_id is not None:
                raise AuditChainIntegrityError(
                    "Non-receipt event contains an unexpected receipt identity."
                )

        if len(receipt_events) != 1:
            raise AuditChainIntegrityError(
                "Audit chain must contain exactly one receipt event."
            )

        if trail.events[-1].event_type != self.RECEIPT_EVENT_TYPE:
            raise AuditChainIntegrityError(
                "Receipt event must occupy the final chain position."
            )

    @staticmethod
    def _validate_actor_consistency(
        trail: RecoveryAuditTrail,
    ) -> None:
        actor_ids = {
            event.actor_id
            for event in trail.events
        }

        if len(actor_ids) != 1:
            raise AuditChainIntegrityError(
                "Audit chain actor identity must remain consistent."
            )

        actor_id = next(iter(actor_ids))

        if actor_id != trail.issuer_id:
            raise AuditChainIntegrityError(
                "Audit chain actor must match the trail issuer."
            )

    @staticmethod
    def _validate_status_progression(
        trail: RecoveryAuditTrail,
    ) -> None:
        ready_seen = False

        for event in trail.events:
            if event.recovery_status.value == "RECOVERY_READY":
                ready_seen = True
                continue

            if ready_seen:
                raise AuditChainIntegrityError(
                    "Recovery status regression detected after RECOVERY_READY."
                )