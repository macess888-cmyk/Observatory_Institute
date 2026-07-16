from typing import Any

from models.historical_admissibility_evidence_trust_assessment import (
    HistoricalAdmissibilityEvidenceTrustAssessment,
)
from services.historical_admissibility_evidence_provenance_manifest_validator import (
    HistoricalAdmissibilityEvidenceProvenanceManifestValidator,
)


class HistoricalAdmissibilityEvidenceTrustAssessmentService:
    def __init__(self) -> None:
        self._validator = (
            HistoricalAdmissibilityEvidenceProvenanceManifestValidator()
        )

    def assess(
        self,
        *,
        assessment_id: str,
        manifest: Any,
        manifest_hash: str,
        trust_status: str,
        confidence_level: str,
        rationale: str,
        policy_version: str,
        assessed_at: str,
    ) -> HistoricalAdmissibilityEvidenceTrustAssessment:
        if manifest is None:
            raise ValueError("manifest is required")

        manifest_is_valid = self._validator.validate(
            manifest=manifest,
            expected_hash=manifest_hash,
        )

        if not manifest_is_valid:
            raise ValueError(
                "manifest_hash does not match the supplied manifest"
            )

        return HistoricalAdmissibilityEvidenceTrustAssessment(
            assessment_id=assessment_id,
            manifest_id=manifest.manifest_id,
            manifest_hash=manifest_hash.strip().lower(),
            trust_status=trust_status,
            confidence_level=confidence_level,
            rationale=rationale,
            policy_version=policy_version,
            assessed_at=assessed_at,
            trust_established=False,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )