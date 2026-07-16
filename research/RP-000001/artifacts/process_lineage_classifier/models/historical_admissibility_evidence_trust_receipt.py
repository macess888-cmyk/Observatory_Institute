from dataclasses import dataclass


_ALLOWED_TRUST_STATUSES = {
    "PASS",
    "HOLD",
    "REJECT",
}

_ALLOWED_CONFIDENCE_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
}

_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalAdmissibilityEvidenceTrustReceipt:
    receipt_id: str
    assessment_id: str
    assessment_hash: str
    manifest_id: str
    manifest_hash: str
    trust_status: str
    confidence_level: str
    policy_version: str
    recorded_at: str
    trust_established: bool = False
    evidence_admitted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "receipt_id": self.receipt_id,
            "assessment_id": self.assessment_id,
            "assessment_hash": self.assessment_hash,
            "manifest_id": self.manifest_id,
            "manifest_hash": self.manifest_hash,
            "trust_status": self.trust_status,
            "confidence_level": self.confidence_level,
            "policy_version": self.policy_version,
            "recorded_at": self.recorded_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        self._validate_hash(
            field_name="assessment_hash",
            value=self.assessment_hash,
        )
        self._validate_hash(
            field_name="manifest_hash",
            value=self.manifest_hash,
        )

        if self.trust_status not in _ALLOWED_TRUST_STATUSES:
            raise ValueError(
                "trust_status must be PASS, HOLD, or REJECT"
            )

        if self.confidence_level not in _ALLOWED_CONFIDENCE_LEVELS:
            raise ValueError(
                "confidence_level must be LOW, MEDIUM, or HIGH"
            )

        if self.trust_established is not False:
            raise ValueError(
                "trust receipt cannot establish trust"
            )

        if self.evidence_admitted is not False:
            raise ValueError(
                "trust receipt cannot admit evidence"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "trust receipt cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "trust receipt cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "trust receipt cannot permit side effects"
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