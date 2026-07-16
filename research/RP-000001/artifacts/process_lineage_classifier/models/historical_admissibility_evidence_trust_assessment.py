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
class HistoricalAdmissibilityEvidenceTrustAssessment:
    assessment_id: str
    manifest_id: str
    manifest_hash: str
    trust_status: str
    confidence_level: str
    rationale: str
    policy_version: str
    assessed_at: str
    trust_established: bool = False
    evidence_admitted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "assessment_id": self.assessment_id,
            "manifest_id": self.manifest_id,
            "manifest_hash": self.manifest_hash,
            "trust_status": self.trust_status,
            "confidence_level": self.confidence_level,
            "rationale": self.rationale,
            "policy_version": self.policy_version,
            "assessed_at": self.assessed_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        normalized_hash = self.manifest_hash.strip().lower()

        if len(normalized_hash) != 64:
            raise ValueError(
                "manifest_hash must contain exactly "
                "64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_hash
        ):
            raise ValueError(
                "manifest_hash must contain only hexadecimal characters"
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
                "trust assessment cannot establish trust"
            )

        if self.evidence_admitted is not False:
            raise ValueError(
                "trust assessment cannot admit evidence"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "trust assessment cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "trust assessment cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "trust assessment cannot permit side effects"
            )