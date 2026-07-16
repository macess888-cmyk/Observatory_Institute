from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)


def make_manifest() -> HistoricalAdmissibilityEvidenceProvenanceManifest:
    return HistoricalAdmissibilityEvidenceProvenanceManifest(
        manifest_id="HAEPM-000001",
        bundle_id="HSAB-000001",
        provenance_hashes=(
            "a" * 64,
            "b" * 64,
        ),
        record_count=2,
        assembled_at="2026-07-16T19:00:00Z",
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_manifest_records_provenance_collection() -> None:
    manifest = make_manifest()

    assert manifest.manifest_id == "HAEPM-000001"
    assert manifest.bundle_id == "HSAB-000001"
    assert manifest.provenance_hashes == (
        "a" * 64,
        "b" * 64,
    )
    assert manifest.record_count == 2
    assert manifest.assembled_at == "2026-07-16T19:00:00Z"


def test_manifest_is_immutable() -> None:
    manifest = make_manifest()

    with pytest.raises(FrozenInstanceError):
        manifest.record_count = 3  # type: ignore[misc]


def test_manifest_requires_at_least_one_provenance_hash() -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(
            manifest_id="HAEPM-000001",
            bundle_id="HSAB-000001",
            provenance_hashes=(),
            record_count=0,
            assembled_at="2026-07-16T19:00:00Z",
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "manifest_id",
        "bundle_id",
        "assembled_at",
    ],
)
def test_manifest_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "manifest_id": "HAEPM-000001",
        "bundle_id": "HSAB-000001",
        "provenance_hashes": ("a" * 64,),
        "record_count": 1,
        "assembled_at": "2026-07-16T19:00:00Z",
        "trust_established": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(**values)


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "",
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_manifest_rejects_invalid_provenance_hash(
    invalid_hash: str,
) -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(
            manifest_id="HAEPM-000001",
            bundle_id="HSAB-000001",
            provenance_hashes=(invalid_hash,),
            record_count=1,
            assembled_at="2026-07-16T19:00:00Z",
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_manifest_rejects_duplicate_provenance_hashes() -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(
            manifest_id="HAEPM-000001",
            bundle_id="HSAB-000001",
            provenance_hashes=(
                "a" * 64,
                "a" * 64,
            ),
            record_count=2,
            assembled_at="2026-07-16T19:00:00Z",
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


@pytest.mark.parametrize(
    "record_count",
    [
        -1,
        0,
        1,
        3,
    ],
)
def test_manifest_requires_record_count_to_match_hashes(
    record_count: int,
) -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(
            manifest_id="HAEPM-000001",
            bundle_id="HSAB-000001",
            provenance_hashes=(
                "a" * 64,
                "b" * 64,
            ),
            record_count=record_count,
            assembled_at="2026-07-16T19:00:00Z",
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_manifest_rejects_non_integer_record_count() -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(
            manifest_id="HAEPM-000001",
            bundle_id="HSAB-000001",
            provenance_hashes=("a" * 64,),
            record_count="1",  # type: ignore[arg-type]
            assembled_at="2026-07-16T19:00:00Z",
            trust_established=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "trust_established",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_manifest_rejects_trust_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "manifest_id": "HAEPM-000001",
        "bundle_id": "HSAB-000001",
        "provenance_hashes": ("a" * 64,),
        "record_count": 1,
        "assembled_at": "2026-07-16T19:00:00Z",
        "trust_established": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceManifest(**values)


def test_manifest_preserves_observer_only_invariants() -> None:
    manifest = make_manifest()

    assert manifest.trust_established is False
    assert manifest.authorization_granted is False
    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False