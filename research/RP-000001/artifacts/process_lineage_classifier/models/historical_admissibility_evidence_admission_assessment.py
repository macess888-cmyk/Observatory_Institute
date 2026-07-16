from dataclasses import dataclass


_ALLOWED_ADMISSION_STATUSES = {
    "PASS",
    "HOLD",
    "REJECT",
}

_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalAdmissibilityEvidenceAdmissionAssessment:
    assessment_id: str
    trust_receipt_id: str
    trust_receipt_hash: str
    admission_status: str
    rationale: str
    policy_version: str
    assessed_at: str
    evidence_admitted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "assessment_id": self.assessment_id,
            "trust_receipt_id": self.trust_receipt_id,
            "trust_receipt_hash": self.trust_receipt_hash,
            "admission_status": self.admission_status,
            "rationale": self.rationale,
            "policy_version": self.policy_version,
            "assessed_at": self.assessed_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        normalized_hash = self.trust_receipt_hash.strip().lower()

        if len(normalized_hash) != 64:
            raise ValueError(
                "trust_receipt_hash must contain exactly "
                "64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_hash
        ):
            raise ValueError(
                "trust_receipt_hash must contain only "
                "hexadecimal characters"
            )

        if self.admission_status not in _ALLOWED_ADMISSION_STATUSES:
            raise ValueError(
                "admission_status must be PASS, HOLD, or REJECT"
            )

        if self.evidence_admitted is not False:
            raise ValueError(
                "admission assessment cannot admit evidence"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "admission assessment cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "admission assessment cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "admission assessment cannot permit side effects"
            )