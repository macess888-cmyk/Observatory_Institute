from typing import Any

from models.historical_admissibility_evidence_package import (
    HistoricalAdmissibilityEvidencePackage,
)
from services.historical_admissibility_evidence_admission_receipt_validator import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptValidator,
)
from services.historical_admissibility_evidence_provenance_manifest_validator import (
    HistoricalAdmissibilityEvidenceProvenanceManifestValidator,
)
from services.historical_admissibility_evidence_trust_receipt_validator import (
    HistoricalAdmissibilityEvidenceTrustReceiptValidator,
)
from services.historical_signature_admissibility_bundle_validator import (
    HistoricalSignatureAdmissibilityBundleValidator,
)


class HistoricalAdmissibilityEvidencePackageService:
    def __init__(self) -> None:
        self._bundle_validator = (
            HistoricalSignatureAdmissibilityBundleValidator()
        )
        self._manifest_validator = (
            HistoricalAdmissibilityEvidenceProvenanceManifestValidator()
        )
        self._trust_receipt_validator = (
            HistoricalAdmissibilityEvidenceTrustReceiptValidator()
        )
        self._admission_receipt_validator = (
            HistoricalAdmissibilityEvidenceAdmissionReceiptValidator()
        )

    def assemble(
        self,
        *,
        package_id: str,
        admissibility_bundle: Any,
        admissibility_bundle_hash: str,
        provenance_manifest: Any,
        provenance_manifest_hash: str,
        trust_receipt: Any,
        trust_receipt_hash: str,
        admission_receipt: Any,
        admission_receipt_hash: str,
        package_version: str,
        assembled_at: str,
    ) -> HistoricalAdmissibilityEvidencePackage:
        components = {
            "admissibility_bundle": admissibility_bundle,
            "provenance_manifest": provenance_manifest,
            "trust_receipt": trust_receipt,
            "admission_receipt": admission_receipt,
        }

        for component_name, component in components.items():
            if component is None:
                raise ValueError(f"{component_name} is required")

        validations = (
            self._bundle_validator.validate(
                bundle=admissibility_bundle,
                expected_hash=admissibility_bundle_hash,
            ),
            self._manifest_validator.validate(
                manifest=provenance_manifest,
                expected_hash=provenance_manifest_hash,
            ),
            self._trust_receipt_validator.validate(
                receipt=trust_receipt,
                expected_hash=trust_receipt_hash,
            ),
            self._admission_receipt_validator.validate(
                receipt=admission_receipt,
                expected_hash=admission_receipt_hash,
            ),
        )

        if not all(validations):
            raise ValueError(
                "one or more component hashes do not match "
                "their supplied components"
            )

        if provenance_manifest.bundle_id != admissibility_bundle.bundle_id:
            raise ValueError(
                "provenance manifest must reference the supplied "
                "admissibility bundle"
            )

        if trust_receipt.manifest_id != provenance_manifest.manifest_id:
            raise ValueError(
                "trust receipt must reference the supplied "
                "provenance manifest"
            )

        if admission_receipt.trust_receipt_id != trust_receipt.receipt_id:
            raise ValueError(
                "admission receipt must reference the supplied "
                "trust receipt"
            )

        return HistoricalAdmissibilityEvidencePackage(
            package_id=package_id,
            admissibility_bundle_id=admissibility_bundle.bundle_id,
            admissibility_bundle_hash=admissibility_bundle_hash.strip().lower(),
            provenance_manifest_id=provenance_manifest.manifest_id,
            provenance_manifest_hash=provenance_manifest_hash.strip().lower(),
            trust_receipt_id=trust_receipt.receipt_id,
            trust_receipt_hash=trust_receipt_hash.strip().lower(),
            admission_receipt_id=admission_receipt.receipt_id,
            admission_receipt_hash=admission_receipt_hash.strip().lower(),
            package_version=package_version,
            assembled_at=assembled_at,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )