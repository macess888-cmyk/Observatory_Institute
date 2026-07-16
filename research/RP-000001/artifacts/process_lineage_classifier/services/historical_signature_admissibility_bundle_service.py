from typing import Any

from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)
from services.historical_signature_admissibility_receipt_validator import (
    HistoricalSignatureAdmissibilityReceiptValidator,
)


class HistoricalSignatureAdmissibilityBundleService:
    def __init__(self) -> None:
        self._validator = HistoricalSignatureAdmissibilityReceiptValidator()

    def create_bundle(
        self,
        *,
        bundle_id: str,
        receipt: Any,
        receipt_hash: str,
        exported_at: str,
    ) -> HistoricalSignatureAdmissibilityBundle:
        if receipt is None:
            raise ValueError("receipt is required")

        receipt_is_valid = self._validator.validate(
            receipt=receipt,
            expected_hash=receipt_hash,
        )

        if not receipt_is_valid:
            raise ValueError(
                "receipt_hash does not match the supplied receipt"
            )

        return HistoricalSignatureAdmissibilityBundle(
            bundle_id=bundle_id,
            receipt_id=receipt.receipt_id,
            receipt_hash=receipt_hash.strip().lower(),
            assessment_hash=receipt.assessment_hash,
            signature_id=receipt.signature_id,
            key_id=receipt.key_id,
            admissibility_status=receipt.admissibility_status,
            policy_version=receipt.policy_version,
            exported_at=exported_at,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )