import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidencePackageReceiptHasher:
    def hash_receipt(
        self,
        receipt: Any,
    ) -> str:
        if receipt is None:
            raise ValueError("receipt is required")

        payload = {
            "authorization_granted": receipt.authorization_granted,
            "evidence_admitted": receipt.evidence_admitted,
            "execution_requested": receipt.execution_requested,
            "package_hash": receipt.package_hash,
            "package_id": receipt.package_id,
            "package_status": receipt.package_status,
            "package_version": receipt.package_version,
            "receipt_id": receipt.receipt_id,
            "recorded_at": receipt.recorded_at,
            "side_effects_permitted": receipt.side_effects_permitted,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()