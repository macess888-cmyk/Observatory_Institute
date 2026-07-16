from typing import Any

from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)
from services.historical_admissibility_evidence_trust_assessment_validator import (
    HistoricalAdmissibilityEvidenceTrustAssessmentValidator,
)


class HistoricalAdmissibilityEvidenceTrustReceiptService:
    def __init__(self) -> None:
        self._validator = (
            HistoricalAdmissibilityEvidenceTrustAssessmentValidator()
        )

    def create_receipt(
        self,
        *,
        receipt_id: str,
        assessment: Any,
        assessment_hash: str,
        recorded_at: str,
    ) -> HistoricalAdmissibilityEvidenceTrustReceipt:
        if assessment is None:
            raise ValueError("assessment is required")

        assessment_is_valid = self._validator.validate(
            assessment=assessment,
            expected_hash=assessment_hash,
        )

        if not assessment_is_valid:
            raise ValueError(
                "assessment_hash does not match the supplied assessment"
            )

        return HistoricalAdmissibilityEvidenceTrustReceipt(
            receipt_id=receipt_id,
            assessment_id=assessment.assessment_id,
            assessment_hash=assessment_hash.strip().lower(),
            manifest_id=assessment.manifest_id,
            manifest_hash=assessment.manifest_hash,
            trust_status=assessment.trust_status,
            confidence_level=assessment.confidence_level,
            policy_version=assessment.policy_version,
            recorded_at=recorded_at,
            trust_established=False,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )