import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidenceTrustReceiptHasher:
    def hash_receipt(
        self,
        receipt: Any,
    ) -> str:
        if receipt is None:
            raise ValueError("receipt is required")

        payload = {
            "assessment_hash": receipt.assessment_hash,
            "assessment_id": receipt.assessment_id,
            "authorization_granted": receipt.authorization_granted,
            "confidence_level": receipt.confidence_level,
            "evidence_admitted": receipt.evidence_admitted,
            "execution_requested": receipt.execution_requested,
            "manifest_hash": receipt.manifest_hash,
            "manifest_id": receipt.manifest_id,
            "policy_version": receipt.policy_version,
            "receipt_id": receipt.receipt_id,
            "recorded_at": receipt.recorded_at,
            "side_effects_permitted": receipt.side_effects_permitted,
            "trust_established": receipt.trust_established,
            "trust_status": receipt.trust_status,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()