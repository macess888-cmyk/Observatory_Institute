import pytest

from models.historical_admissibility_evidence_provenance import (
    HistoricalAdmissibilityEvidenceProvenance,
)
from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)
from services.historical_admissibility_evidence_provenance_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceHasher,
)
from services.historical_admissibility_evidence_provenance_manifest_service import (
    HistoricalAdmissibilityEvidenceProvenanceManifestService,
)


def make_provenance(
    *,
    provenance_id: str,
    evidence_id: str,
    source_hash: str,
) -> HistoricalAdmissibilityEvidenceProvenance:
    return HistoricalAdmissibilityEvidenceProvenance(
        provenance_id=provenance_id,
        bundle_id="HSAB-000001",
        evidence_id=evidence_id,
        evidence_type="KEY_COMPROMISE_EVENT",
        source_system="historical-key-registry",
        source_reference=f"registry://evidence/{evidence_id}",
        source_hash=source_hash,
        observed_at="2026-07-16T18:30:00Z",
        collected_at="2026-07-16T18:35:00Z",
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_records() -> tuple[
    HistoricalAdmissibilityEvidenceProvenance,
    HistoricalAdmissibilityEvidenceProvenance,
]:
    return (
        make_provenance(
            provenance_id="HAEP-000001",
            evidence_id="EVD-000001",
            source_hash="a" * 64,
        ),
        make_provenance(
            provenance_id="HAEP-000002",
            evidence_id="EVD-000002",
            source_hash="b" * 64,
        ),
    )


def test_service_creates_manifest_from_provenance_records() -> None:
    records = make_records()
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    manifest = (
        HistoricalAdmissibilityEvidenceProvenanceManifestService()
        .create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=records,
            assembled_at="2026-07-16T19:00:00Z",
        )
    )

    assert isinstance(
        manifest,
        HistoricalAdmissibilityEvidenceProvenanceManifest,
    )
    assert manifest.manifest_id == "HAEPM-000001"
    assert manifest.bundle_id == "HSAB-000001"
    assert manifest.provenance_hashes == (
        hasher.hash_provenance(records[0]),
        hasher.hash_provenance(records[1]),
    )
    assert manifest.record_count == 2
    assert manifest.assembled_at == "2026-07-16T19:00:00Z"


def test_service_rejects_empty_provenance_collection() -> None:
    service = HistoricalAdmissibilityEvidenceProvenanceManifestService()

    with pytest.raises(ValueError):
        service.create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=(),
            assembled_at="2026-07-16T19:00:00Z",
        )


def test_service_rejects_none_provenance_collection() -> None:
    service = HistoricalAdmissibilityEvidenceProvenanceManifestService()

    with pytest.raises(ValueError):
        service.create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=None,
            assembled_at="2026-07-16T19:00:00Z",
        )


def test_service_rejects_none_record() -> None:
    records = (
        make_records()[0],
        None,
    )

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifestService().create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=records,
            assembled_at="2026-07-16T19:00:00Z",
        )


def test_service_rejects_records_from_different_bundles() -> None:
    first = make_records()[0]

    second = HistoricalAdmissibilityEvidenceProvenance(
        provenance_id="HAEP-000002",
        bundle_id="HSAB-000002",
        evidence_id="EVD-000002",
        evidence_type="KEY_COMPROMISE_EVENT",
        source_system="historical-key-registry",
        source_reference="registry://evidence/EVD-000002",
        source_hash="b" * 64,
        observed_at="2026-07-16T18:30:00Z",
        collected_at="2026-07-16T18:35:00Z",
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifestService().create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=(first, second),
            assembled_at="2026-07-16T19:00:00Z",
        )


def test_service_rejects_duplicate_provenance_records() -> None:
    record = make_records()[0]

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifestService().create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=(record, record),
            assembled_at="2026-07-16T19:00:00Z",
        )


def test_service_preserves_input_order() -> None:
    records = make_records()
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    manifest = (
        HistoricalAdmissibilityEvidenceProvenanceManifestService()
        .create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=records,
            assembled_at="2026-07-16T19:00:00Z",
        )
    )

    assert manifest.provenance_hashes == tuple(
        hasher.hash_provenance(record)
        for record in records
    )


def test_service_preserves_observer_only_invariants() -> None:
    manifest = (
        HistoricalAdmissibilityEvidenceProvenanceManifestService()
        .create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=make_records(),
            assembled_at="2026-07-16T19:00:00Z",
        )
    )

    assert manifest.trust_established is False
    assert manifest.authorization_granted is False
    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False


def test_service_does_not_mutate_provenance_records() -> None:
    records = make_records()
    originals = tuple(records)

    HistoricalAdmissibilityEvidenceProvenanceManifestService().create_manifest(
        manifest_id="HAEPM-000001",
        provenance_records=records,
        assembled_at="2026-07-16T19:00:00Z",
    )

    assert records == originals

    for record in records:
        assert record.trust_established is False
        assert record.authorization_granted is False
        assert record.execution_requested is False
        assert record.side_effects_permitted is False