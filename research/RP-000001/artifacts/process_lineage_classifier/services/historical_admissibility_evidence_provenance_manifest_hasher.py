import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidenceProvenanceManifestHasher:
    def hash_manifest(
        self,
        manifest: Any,
    ) -> str:
        if manifest is None:
            raise ValueError("manifest is required")

        payload = {
            "assembled_at": manifest.assembled_at,
            "authorization_granted": manifest.authorization_granted,
            "bundle_id": manifest.bundle_id,
            "execution_requested": manifest.execution_requested,
            "manifest_id": manifest.manifest_id,
            "provenance_hashes": list(manifest.provenance_hashes),
            "record_count": manifest.record_count,
            "side_effects_permitted": manifest.side_effects_permitted,
            "trust_established": manifest.trust_established,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()