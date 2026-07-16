from dataclasses import dataclass


_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class HistoricalAdmissibilityEvidenceProvenanceManifest:
    manifest_id: str
    bundle_id: str
    provenance_hashes: tuple[str, ...]
    record_count: int
    assembled_at: str
    trust_established: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        required_fields = {
            "manifest_id": self.manifest_id,
            "bundle_id": self.bundle_id,
            "assembled_at": self.assembled_at,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

        if not isinstance(self.provenance_hashes, tuple):
            raise ValueError("provenance_hashes must be a tuple")

        if not self.provenance_hashes:
            raise ValueError(
                "provenance_hashes must contain at least one hash"
            )

        normalized_hashes: list[str] = []

        for provenance_hash in self.provenance_hashes:
            if not isinstance(provenance_hash, str):
                raise ValueError(
                    "each provenance hash must be a string"
                )

            normalized_hash = provenance_hash.strip().lower()

            if len(normalized_hash) != 64:
                raise ValueError(
                    "each provenance hash must contain exactly "
                    "64 hexadecimal characters"
                )

            if any(
                character not in _HEX_DIGITS
                for character in normalized_hash
            ):
                raise ValueError(
                    "each provenance hash must contain only "
                    "hexadecimal characters"
                )

            normalized_hashes.append(normalized_hash)

        if len(set(normalized_hashes)) != len(normalized_hashes):
            raise ValueError(
                "provenance_hashes must not contain duplicates"
            )

        if not isinstance(self.record_count, int) or isinstance(
            self.record_count,
            bool,
        ):
            raise ValueError("record_count must be an integer")

        if self.record_count != len(self.provenance_hashes):
            raise ValueError(
                "record_count must match the number of provenance hashes"
            )

        if self.trust_established is not False:
            raise ValueError(
                "provenance manifest cannot establish trust"
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "provenance manifest cannot grant authorization"
            )

        if self.execution_requested is not False:
            raise ValueError(
                "provenance manifest cannot request execution"
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "provenance manifest cannot permit side effects"
            )