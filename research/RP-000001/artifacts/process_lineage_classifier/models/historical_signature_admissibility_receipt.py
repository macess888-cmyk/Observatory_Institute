from dataclasses import dataclass


_ALLOWED_ADMISSIBILITY_STATUSES = {
    "PASS",
    "HOLD",
    "REJECT",
}


@dataclass(frozen=True)
class HistoricalSignatureAdmissibilityReceipt:
    receipt_id: str
    assessment_hash: str
    signature_id: str
    key_id: str
    admissibility_status: str
    policy_version: str
    recorded_at: str
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "receipt_id": self.receipt_id,
            "assessment_hash": self.assessment_hash,
            "signature_id": self.signature_id,
            "key_id": self.key_id,
            "admissibility_status": self.admissibility_status,
            "policy_version": self.policy_version,
            "recorded_at": self.recorded_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        if self.admissibility_status not in _ALLOWED_ADMISSIBILITY_STATUSES:
            raise ValueError(
                "admissibility_status must be PASS, HOLD, or REJECT"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "historical admissibility receipt cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "historical admissibility receipt cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "historical admissibility receipt cannot permit side effects"
            )