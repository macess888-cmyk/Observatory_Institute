import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidencePackageHasher:
    def hash_package(
        self,
        package: Any,
    ) -> str:
        if package is None:
            raise ValueError("package is required")

        payload = {
            "admissibility_bundle_hash": package.admissibility_bundle_hash,
            "admissibility_bundle_id": package.admissibility_bundle_id,
            "admission_receipt_hash": package.admission_receipt_hash,
            "admission_receipt_id": package.admission_receipt_id,
            "assembled_at": package.assembled_at,
            "authorization_granted": package.authorization_granted,
            "evidence_admitted": package.evidence_admitted,
            "execution_requested": package.execution_requested,
            "package_id": package.package_id,
            "package_version": package.package_version,
            "provenance_manifest_hash": package.provenance_manifest_hash,
            "provenance_manifest_id": package.provenance_manifest_id,
            "side_effects_permitted": package.side_effects_permitted,
            "trust_receipt_hash": package.trust_receipt_hash,
            "trust_receipt_id": package.trust_receipt_id,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()