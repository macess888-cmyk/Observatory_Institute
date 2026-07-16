from dataclasses import dataclass


_ALLOWED_PACKAGE_STATUSES = {
    "PASS",
    "HOLD",
    "REJECT",
}

_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalAdmissibilityEvidencePackageReceipt:
    receipt_id: str
    package_id: str
    package_hash: str
    package_status: str
    package_version: str
    recorded_at: str
    evidence_admitted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "receipt_id": self.receipt_id,
            "package_id": self.package_id,
            "package_hash": self.package_hash,
            "package_status": self.package_status,
            "package_version": self.package_version,
            "recorded_at": self.recorded_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        normalized_hash = self.package_hash.strip().lower()

        if len(normalized_hash) != 64:
            raise ValueError(
                "package_hash must contain exactly "
                "64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_hash
        ):
            raise ValueError(
                "package_hash must contain only hexadecimal characters"
            )

        if self.package_status not in _ALLOWED_PACKAGE_STATUSES:
            raise ValueError(
                "package_status must be PASS, HOLD, or REJECT"
            )

        if self.evidence_admitted is not False:
            raise ValueError(
                "package receipt cannot admit evidence"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "package receipt cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "package receipt cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "package receipt cannot permit side effects"
            )