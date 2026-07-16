from typing import Any

from models.historical_admissibility_evidence_provenance import (
    HistoricalAdmissibilityEvidenceProvenance,
)


class HistoricalAdmissibilityEvidenceProvenanceService:
    def create_provenance(
        self,
        *,
        provenance_id: str,
        bundle: Any,
        evidence_id: str,
        evidence_type: str,
        source_system: str,
        source_reference: str,
        source_hash: str,
        observed_at: str,
        collected_at: str,
    ) -> HistoricalAdmissibilityEvidenceProvenance:
        if bundle is None:
            raise ValueError("bundle is required")

        if not hasattr(bundle, "bundle_id"):
            raise ValueError("bundle must provide bundle_id")

        return HistoricalAdmissibilityEvidenceProvenance(
            provenance_id=provenance_id,
            bundle_id=bundle.bundle_id,
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            source_system=source_system,
            source_reference=source_reference,
            source_hash=source_hash,
            observed_at=observed_at,
            collected_at=collected_at,
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )