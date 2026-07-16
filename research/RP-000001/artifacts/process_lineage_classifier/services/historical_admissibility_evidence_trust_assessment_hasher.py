import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidenceTrustAssessmentHasher:
    def hash_assessment(
        self,
        assessment: Any,
    ) -> str:
        if assessment is None:
            raise ValueError("assessment is required")

        payload = {
            "assessed_at": assessment.assessed_at,
            "assessment_id": assessment.assessment_id,
            "authorization_granted": assessment.authorization_granted,
            "confidence_level": assessment.confidence_level,
            "evidence_admitted": assessment.evidence_admitted,
            "execution_requested": assessment.execution_requested,
            "manifest_hash": assessment.manifest_hash,
            "manifest_id": assessment.manifest_id,
            "policy_version": assessment.policy_version,
            "rationale": assessment.rationale,
            "side_effects_permitted": assessment.side_effects_permitted,
            "trust_established": assessment.trust_established,
            "trust_status": assessment.trust_status,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()