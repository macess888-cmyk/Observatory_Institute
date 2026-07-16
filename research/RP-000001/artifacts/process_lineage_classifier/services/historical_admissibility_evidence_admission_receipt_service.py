from typing import Any

from models.historical_admissibility_evidence_admission_receipt import (
    HistoricalAdmissibilityEvidenceAdmissionReceipt,
)
from services.historical_admissibility_evidence_admission_assessment_validator import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator,
)


class HistoricalAdmissibilityEvidenceAdmissionReceiptService:
    def __init__(self) -> None:
        self._validator = (
            HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()
        )

    def create_receipt(
        self,
        *,
        receipt_id: str,
        assessment: Any,
        assessment_hash: str,
        recorded_at: str,
    ) -> HistoricalAdmissibilityEvidenceAdmissionReceipt:
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

        return HistoricalAdmissibilityEvidenceAdmissionReceipt(
            receipt_id=receipt_id,
            assessment_id=assessment.assessment_id,
            assessment_hash=assessment_hash.strip().lower(),
            trust_receipt_id=assessment.trust_receipt_id,
            trust_receipt_hash=assessment.trust_receipt_hash,
            admission_status=assessment.admission_status,
            policy_version=assessment.policy_version,
            recorded_at=recorded_at,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )