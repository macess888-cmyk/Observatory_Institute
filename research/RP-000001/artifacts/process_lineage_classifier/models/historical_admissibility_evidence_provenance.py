from dataclasses import dataclass


_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalAdmissibilityEvidenceProvenance:
    provenance_id: str
    bundle_id: str
    evidence_id: str
    evidence_type: str
    source_system: str
    source_reference: str
    source_hash: str
    observed_at: str
    collected_at: str
    trust_established: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "provenance_id": self.provenance_id,
            "bundle_id": self.bundle_id,
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "source_system": self.source_system,
            "source_reference": self.source_reference,
            "source_hash": self.source_hash,
            "observed_at": self.observed_at,
            "collected_at": self.collected_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        normalized_hash = self.source_hash.lower()

        if len(normalized_hash) != 64:
            raise ValueError(
                "source_hash must contain exactly 64 hexadecimal characters"
            )

        if any(
            character not in _HEX_DIGITS
            for character in normalized_hash
        ):
            raise ValueError(
                "source_hash must contain only hexadecimal characters"
            )

        if self.trust_established is not False:
            raise ValueError(
                "historical evidence provenance cannot establish trust"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "historical evidence provenance cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "historical evidence provenance cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "historical evidence provenance cannot permit side effects"
            )