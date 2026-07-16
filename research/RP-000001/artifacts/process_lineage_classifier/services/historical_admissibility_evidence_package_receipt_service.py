from typing import Any

from models.historical_admissibility_evidence_package_receipt import (
    HistoricalAdmissibilityEvidencePackageReceipt,
)
from services.historical_admissibility_evidence_package_validator import (
    HistoricalAdmissibilityEvidencePackageValidator,
)


class HistoricalAdmissibilityEvidencePackageReceiptService:
    def __init__(self) -> None:
        self._validator = HistoricalAdmissibilityEvidencePackageValidator()

    def create_receipt(
        self,
        *,
        receipt_id: str,
        package: Any,
        package_hash: str,
        package_status: str,
        recorded_at: str,
    ) -> HistoricalAdmissibilityEvidencePackageReceipt:
        if package is None:
            raise ValueError("package is required")

        package_is_valid = self._validator.validate(
            package=package,
            expected_hash=package_hash,
        )

        if not package_is_valid:
            raise ValueError(
                "package_hash does not match the supplied package"
            )

        return HistoricalAdmissibilityEvidencePackageReceipt(
            receipt_id=receipt_id,
            package_id=package.package_id,
            package_hash=package_hash.strip().lower(),
            package_status=package_status,
            package_version=package.package_version,
            recorded_at=recorded_at,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )