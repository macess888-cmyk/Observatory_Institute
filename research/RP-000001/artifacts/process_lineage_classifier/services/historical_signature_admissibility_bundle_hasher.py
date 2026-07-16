import hashlib
import json
from typing import Any


class HistoricalSignatureAdmissibilityBundleHasher:
    def hash_bundle(
        self,
        bundle: Any,
    ) -> str:
        if bundle is None:
            raise ValueError("bundle is required")

        payload = {
            "admissibility_status": bundle.admissibility_status,
            "assessment_hash": bundle.assessment_hash,
            "authorization_granted": bundle.authorization_granted,
            "bundle_id": bundle.bundle_id,
            "execution_requested": bundle.execution_requested,
            "exported_at": bundle.exported_at,
            "key_id": bundle.key_id,
            "policy_version": bundle.policy_version,
            "receipt_hash": bundle.receipt_hash,
            "receipt_id": bundle.receipt_id,
            "side_effects_permitted": bundle.side_effects_permitted,
            "signature_id": bundle.signature_id,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()