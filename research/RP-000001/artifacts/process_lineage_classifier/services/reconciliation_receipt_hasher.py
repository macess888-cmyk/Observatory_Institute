import hashlib
import json

from models import (
    ReconciliationReceipt,
    ReconciliationReceiptHash,
)


class ReconciliationReceiptHashingError(ValueError):
    """Raised when a reconciliation receipt cannot be hashed."""


class ReconciliationReceiptHasher:
    """Produces deterministic SHA-256 hashes for reconciliation receipts."""

    ALGORITHM = "sha256"

    def hash(
        self,
        receipt: ReconciliationReceipt,
    ) -> ReconciliationReceiptHash:
        if not isinstance(receipt, ReconciliationReceipt):
            raise TypeError(
                "receipt must be a ReconciliationReceipt."
            )

        canonical_payload = self._canonicalize(receipt)

        digest_value = hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()

        return ReconciliationReceiptHash(
            receipt_id=receipt.receipt_id,
            algorithm=self.ALGORITHM,
            digest=f"{self.ALGORITHM}:{digest_value}",
            canonical_payload=canonical_payload,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _canonicalize(
        receipt: ReconciliationReceipt,
    ) -> str:
        payload = {
            "receipt_id": receipt.receipt_id,
            "recovery_status": receipt.recovery_status.value,
            "operational_status": receipt.operational_status.value,
            "confidence": receipt.confidence.value,
            "assessment_types": [
                event_type.value
                for event_type in receipt.assessment_types
            ],
            "assessment_ids": list(receipt.assessment_ids),
            "evidence_ids": list(receipt.evidence_ids),
            "applied_rules": list(receipt.applied_rules),
            "reasons": list(receipt.reasons),
            "missing_evidence": list(receipt.missing_evidence),
            "conflicts": list(receipt.conflicts),
            "issued_at": receipt.issued_at.isoformat(),
            "issuer_id": receipt.issuer_id,
            "execution_requested": receipt.execution_requested,
            "side_effects_permitted": receipt.side_effects_permitted,
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=False,
        )