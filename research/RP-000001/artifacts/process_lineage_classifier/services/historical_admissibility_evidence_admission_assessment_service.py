from typing import Any

from models.historical_admissibility_evidence_admission_assessment import (
    HistoricalAdmissibilityEvidenceAdmissionAssessment,
)
from services.historical_admissibility_evidence_trust_receipt_validator import (
    HistoricalAdmissibilityEvidenceTrustReceiptValidator,
)


class HistoricalAdmissibilityEvidenceAdmissionAssessmentService:
    def __init__(self) -> None:
        self._validator = (
            HistoricalAdmissibilityEvidenceTrustReceiptValidator()
        )

    def assess(
        self,
        *,
        assessment_id: str,
        trust_receipt: Any,
        trust_receipt_hash: str,
        admission_status: str,
        rationale: str,
        policy_version: str,
        assessed_at: str,
    ) -> HistoricalAdmissibilityEvidenceAdmissionAssessment:
        if trust_receipt is None:
            raise ValueError("trust_receipt is required")

        receipt_is_valid = self._validator.validate(
            receipt=trust_receipt,
            expected_hash=trust_receipt_hash,
        )

        if not receipt_is_valid:
            raise ValueError(
                "trust_receipt_hash does not match the supplied trust receipt"
            )

        return HistoricalAdmissibilityEvidenceAdmissionAssessment(
            assessment_id=assessment_id,
            trust_receipt_id=trust_receipt.receipt_id,
            trust_receipt_hash=trust_receipt_hash.strip().lower(),
            admission_status=admission_status,
            rationale=rationale,
            policy_version=policy_version,
            assessed_at=assessed_at,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )