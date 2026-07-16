from dataclasses import dataclass


_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalAdmissibilityEvidencePackage:
    package_id: str
    admissibility_bundle_id: str
    admissibility_bundle_hash: str
    provenance_manifest_id: str
    provenance_manifest_hash: str
    trust_receipt_id: str
    trust_receipt_hash: str
    admission_receipt_id: str
    admission_receipt_hash: str
    package_version: str
    assembled_at: str
    evidence_admitted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "package_id": self.package_id,
            "admissibility_bundle_id": self.admissibility_bundle_id,
            "admissibility_bundle_hash": self.admissibility_bundle_hash,
            "provenance_manifest_id": self.provenance_manifest_id,
            "provenance_manifest_hash": self.provenance_manifest_hash,
            "trust_receipt_id": self.trust_receipt_id,
            "trust_receipt_hash": self.trust_receipt_hash,
            "admission_receipt_id": self.admission_receipt_id,
            "admission_receipt_hash": self.admission_receipt_hash,
            "package_version": self.package_version,
            "assembled_at": self.assembled_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        hashes = {
            "admissibility_bundle_hash": self.admissibility_bundle_hash,
            "provenance_manifest_hash": self.provenance_manifest_hash,
            "trust_receipt_hash": self.trust_receipt_hash,
            "admission_receipt_hash": self.admission_receipt_hash,
        }

        for field_name, value in hashes.items():
            self._validate_hash(
                field_name=field_name,
                value=value,
            )

        if self.evidence_admitted is not False:
            raise ValueError(
                "historical evidence package cannot admit evidence"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "historical evidence package cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "historical evidence package cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "historical evidence package cannot permit side effects"
            )

    @staticmethod
    def _validate_hash(
        *,
        field_name: str,
        value: str,
    ) -> None:
        normalized_value = value.strip().lower()

        if len(normalized_value) != 64:
            raise ValueError(
                f"{field_name} must contain exactly "
                "64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_value
        ):
            raise ValueError(
                f"{field_name} must contain only hexadecimal characters"
            )