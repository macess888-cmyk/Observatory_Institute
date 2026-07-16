import hashlib
import json
from typing import Any


class HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher:
    def hash_assessment(
        self,
        assessment: Any,
    ) -> str:
        if assessment is None:
            raise ValueError("assessment is required")

        payload = {
            "admission_status": assessment.admission_status,
            "assessed_at": assessment.assessed_at,
            "assessment_id": assessment.assessment_id,
            "authorization_granted": assessment.authorization_granted,
            "evidence_admitted": assessment.evidence_admitted,
            "execution_requested": assessment.execution_requested,
            "policy_version": assessment.policy_version,
            "rationale": assessment.rationale,
            "side_effects_permitted": assessment.side_effects_permitted,
            "trust_receipt_hash": assessment.trust_receipt_hash,
            "trust_receipt_id": assessment.trust_receipt_id,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()