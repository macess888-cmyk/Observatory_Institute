from typing import Any

from models.historical_signature_admissibility_receipt import (
    HistoricalSignatureAdmissibilityReceipt,
)


_REQUIRED_ASSESSMENT_ATTRIBUTES = (
    "assessment_hash",
    "signature_id",
    "key_id",
    "admissibility_status",
    "policy_version",
)


class HistoricalSignatureAdmissibilityReceiptService:
    def create_receipt(
        self,
        *,
        receipt_id: str,
        assessment: Any,
        recorded_at: str,
    ) -> HistoricalSignatureAdmissibilityReceipt:
        if assessment is None:
            raise ValueError("assessment is required")

        missing_attributes = [
            attribute_name
            for attribute_name in _REQUIRED_ASSESSMENT_ATTRIBUTES
            if not hasattr(assessment, attribute_name)
        ]

        if missing_attributes:
            missing = ", ".join(missing_attributes)
            raise ValueError(
                f"assessment is missing required attributes: {missing}"
            )

        return HistoricalSignatureAdmissibilityReceipt(
            receipt_id=receipt_id,
            assessment_hash=assessment.assessment_hash,
            signature_id=assessment.signature_id,
            key_id=assessment.key_id,
            admissibility_status=assessment.admissibility_status,
            policy_version=assessment.policy_version,
            recorded_at=recorded_at,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )