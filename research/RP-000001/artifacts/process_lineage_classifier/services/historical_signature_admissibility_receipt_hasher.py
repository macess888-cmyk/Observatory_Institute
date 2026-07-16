import hashlib
import json
from typing import Any


class HistoricalSignatureAdmissibilityReceiptHasher:
    def hash_receipt(
        self,
        receipt: Any,
    ) -> str:
        if receipt is None:
            raise ValueError("receipt is required")

        payload = {
            "admissibility_status": receipt.admissibility_status,
            "assessment_hash": receipt.assessment_hash,
            "authorization_granted": receipt.authorization_granted,
            "execution_requested": receipt.execution_requested,
            "key_id": receipt.key_id,
            "policy_version": receipt.policy_version,
            "receipt_id": receipt.receipt_id,
            "recorded_at": receipt.recorded_at,
            "side_effects_permitted": receipt.side_effects_permitted,
            "signature_id": receipt.signature_id,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()