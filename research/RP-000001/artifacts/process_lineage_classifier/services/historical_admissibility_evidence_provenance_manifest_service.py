from collections.abc import Sequence
from typing import Any

from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)
from services.historical_admissibility_evidence_provenance_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceHasher,
)


class HistoricalAdmissibilityEvidenceProvenanceManifestService:
    def __init__(self) -> None:
        self._hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    def create_manifest(
        self,
        *,
        manifest_id: str,
        provenance_records: Sequence[Any] | None,
        assembled_at: str,
    ) -> HistoricalAdmissibilityEvidenceProvenanceManifest:
        if provenance_records is None:
            raise ValueError("provenance_records are required")

        records = tuple(provenance_records)

        if not records:
            raise ValueError(
                "provenance_records must contain at least one record"
            )

        if any(record is None for record in records):
            raise ValueError(
                "provenance_records must not contain None"
            )

        required_attributes = (
            "provenance_id",
            "bundle_id",
        )

        for record in records:
            missing_attributes = [
                attribute_name
                for attribute_name in required_attributes
                if not hasattr(record, attribute_name)
            ]

            if missing_attributes:
                missing = ", ".join(missing_attributes)
                raise ValueError(
                    "provenance record is missing required attributes: "
                    f"{missing}"
                )

        bundle_ids = {
            record.bundle_id
            for record in records
        }

        if len(bundle_ids) != 1:
            raise ValueError(
                "all provenance records must reference the same bundle"
            )

        provenance_ids = [
            record.provenance_id
            for record in records
        ]

        if len(set(provenance_ids)) != len(provenance_ids):
            raise ValueError(
                "provenance_records must not contain duplicates"
            )

        provenance_hashes = tuple(
            self._hasher.hash_provenance(record)
            for record in records
        )

        return HistoricalAdmissibilityEvidenceProvenanceManifest(
            manifest_id=manifest_id,
            bundle_id=records[0].bundle_id,
            provenance_hashes=provenance_hashes,
            record_count=len(records),
            assembled_at=assembled_at,
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )