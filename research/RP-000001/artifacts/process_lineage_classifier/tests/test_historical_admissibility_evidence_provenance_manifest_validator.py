import pytest

from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)
from services.historical_admissibility_evidence_provenance_manifest_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceManifestHasher,
)
from services.historical_admissibility_evidence_provenance_manifest_validator import (
    HistoricalAdmissibilityEvidenceProvenanceManifestValidator,
)


def make_manifest(
    *,
    manifest_id: str = "HAEPM-000001",
    bundle_id: str = "HSAB-000001",
    provenance_hashes: tuple[str, ...] = (
        "a" * 64,
        "b" * 64,
    ),
    record_count: int = 2,
    assembled_at: str = "2026-07-16T19:00:00Z",
) -> HistoricalAdmissibilityEvidenceProvenanceManifest:
    return HistoricalAdmissibilityEvidenceProvenanceManifest(
        manifest_id=manifest_id,
        bundle_id=bundle_id,
        provenance_hashes=provenance_hashes,
        record_count=record_count,
        assembled_at=assembled_at,
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_manifest_hash() -> None:
    manifest = make_manifest()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    assert validator.validate(
        manifest=manifest,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_manifest_hash() -> None:
    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    assert validator.validate(
        manifest=make_manifest(),
        expected_hash="c" * 64,
    ) is False


def test_validator_detects_modified_manifest() -> None:
    original = make_manifest()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(original)
    )

    modified = make_manifest(
        assembled_at="2026-07-16T19:01:00Z",
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    assert validator.validate(
        manifest=modified,
        expected_hash=expected_hash,
    ) is False


def test_validator_detects_reordered_provenance_hashes() -> None:
    original = make_manifest()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(original)
    )

    reordered = make_manifest(
        provenance_hashes=(
            "b" * 64,
            "a" * 64,
        ),
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    assert validator.validate(
        manifest=reordered,
        expected_hash=expected_hash,
    ) is False


def test_validator_rejects_none_manifest() -> None:
    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    with pytest.raises(ValueError):
        validator.validate(
            manifest=None,
            expected_hash="a" * 64,
        )


@pytest.mark.parametrize(
    "expected_hash",
    [
        None,
        "",
        " ",
        "abc",
        "g" * 64,
        "a" * 63,
        "a" * 65,
    ],
)
def test_validator_rejects_invalid_expected_hash(
    expected_hash: str | None,
) -> None:
    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    with pytest.raises(ValueError):
        validator.validate(
            manifest=make_manifest(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    manifest = make_manifest()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    assert validator.validate(
        manifest=manifest,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_manifest() -> None:
    manifest = make_manifest()
    original = manifest

    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
    )

    HistoricalAdmissibilityEvidenceProvenanceManifestValidator().validate(
        manifest=manifest,
        expected_hash=expected_hash,
    )

    assert manifest == original
    assert manifest.trust_established is False
    assert manifest.authorization_granted is False
    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False


def test_successful_validation_does_not_establish_trust() -> None:
    manifest = make_manifest()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceManifestValidator()

    assert validator.validate(
        manifest=manifest,
        expected_hash=expected_hash,
    ) is True

    assert manifest.trust_established is False
    assert manifest.authorization_granted is False
    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False