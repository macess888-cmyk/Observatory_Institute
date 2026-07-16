import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidenceAdmissionReceiptHasher:
    def hash_receipt(
        self,
        receipt: Any,
    ) -> str:
        if receipt is None:
            raise ValueError("receipt is required")

        payload = {
            "admission_status": receipt.admission_status,
            "assessment_hash": receipt.assessment_hash,
            "assessment_id": receipt.assessment_id,
            "authorization_granted": receipt.authorization_granted,
            "evidence_admitted": receipt.evidence_admitted,
            "execution_requested": receipt.execution_requested,
            "policy_version": receipt.policy_version,
            "receipt_id": receipt.receipt_id,
            "recorded_at": receipt.recorded_at,
            "side_effects_permitted": receipt.side_effects_permitted,
            "trust_receipt_hash": receipt.trust_receipt_hash,
            "trust_receipt_id": receipt.trust_receipt_id,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()