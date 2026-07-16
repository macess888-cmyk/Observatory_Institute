from dataclasses import dataclass


_ALLOWED_ADMISSIBILITY_STATUSES = {
    "PASS",
    "HOLD",
    "REJECT",
}

_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalSignatureAdmissibilityBundle:
    bundle_id: str
    receipt_id: str
    receipt_hash: str
    assessment_hash: str
    signature_id: str
    key_id: str
    admissibility_status: str
    policy_version: str
    exported_at: str
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "bundle_id": self.bundle_id,
            "receipt_id": self.receipt_id,
            "receipt_hash": self.receipt_hash,
            "assessment_hash": self.assessment_hash,
            "signature_id": self.signature_id,
            "key_id": self.key_id,
            "admissibility_status": self.admissibility_status,
            "policy_version": self.policy_version,
            "exported_at": self.exported_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        self._validate_hash(
            field_name="receipt_hash",
            value=self.receipt_hash,
        )
        self._validate_hash(
            field_name="assessment_hash",
            value=self.assessment_hash,
        )

        if self.admissibility_status not in _ALLOWED_ADMISSIBILITY_STATUSES:
            raise ValueError(
                "admissibility_status must be PASS, HOLD, or REJECT"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "historical admissibility bundle cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "historical admissibility bundle cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "historical admissibility bundle cannot permit side effects"
            )

    @staticmethod
    def _validate_hash(
        *,
        field_name: str,
        value: str,
    ) -> None:
        normalized_value = value.lower()

        if len(normalized_value) != 64:
            raise ValueError(
                f"{field_name} must contain exactly 64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_value
        ):
            raise ValueError(
                f"{field_name} must contain only hexadecimal characters"
            )