import hashlib
import json

from models import (
    RecoveryAuditEvent,
    RecoveryAuditEventHash,
)


class RecoveryAuditEventHashingError(ValueError):
    """Raised when a recovery audit event cannot be hashed."""


class RecoveryAuditEventHasher:
    """Produces deterministic SHA-256 hashes for recovery audit events."""

    ALGORITHM = "sha256"

    def hash(
        self,
        event: RecoveryAuditEvent,
    ) -> RecoveryAuditEventHash:
        if not isinstance(event, RecoveryAuditEvent):
            raise TypeError(
                "event must be a RecoveryAuditEvent."
            )

        canonical_payload = self._canonicalize(event)

        digest_value = hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()

        return RecoveryAuditEventHash(
            event_id=event.event_id,
            algorithm=self.ALGORITHM,
            digest=f"{self.ALGORITHM}:{digest_value}",
            canonical_payload=canonical_payload,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _canonicalize(
        event: RecoveryAuditEvent,
    ) -> str:
        payload = {
            "event_id": event.event_id,
            "sequence_number": event.sequence_number,
            "event_type": event.event_type,
            "recovery_status": event.recovery_status.value,
            "operational_status": event.operational_status.value,
            "confidence": event.confidence.value,
            "occurred_at": event.occurred_at.isoformat(),
            "actor_id": event.actor_id,
            "related_receipt_id": event.related_receipt_id,
            "evidence_ids": list(event.evidence_ids),
            "reasons": list(event.reasons),
            "conflicts": list(event.conflicts),
            "execution_requested": event.execution_requested,
            "side_effects_permitted": event.side_effects_permitted,
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=False,
        )