import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidenceProvenanceHasher:
    def hash_provenance(
        self,
        provenance: Any,
    ) -> str:
        if provenance is None:
            raise ValueError("provenance is required")

        payload = {
            "authorization_granted": provenance.authorization_granted,
            "bundle_id": provenance.bundle_id,
            "collected_at": provenance.collected_at,
            "evidence_id": provenance.evidence_id,
            "evidence_type": provenance.evidence_type,
            "execution_requested": provenance.execution_requested,
            "observed_at": provenance.observed_at,
            "provenance_id": provenance.provenance_id,
            "side_effects_permitted": provenance.side_effects_permitted,
            "source_hash": provenance.source_hash,
            "source_reference": provenance.source_reference,
            "source_system": provenance.source_system,
            "trust_established": provenance.trust_established,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()