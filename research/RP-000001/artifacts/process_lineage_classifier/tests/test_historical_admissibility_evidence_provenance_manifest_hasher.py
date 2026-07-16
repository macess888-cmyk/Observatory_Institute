import hashlib
import json

import pytest

from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)
from services.historical_admissibility_evidence_provenance_manifest_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceManifestHasher,
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


def expected_hash(
    manifest: HistoricalAdmissibilityEvidenceProvenanceManifest,
) -> str:
    payload = {
        "assembled_at": manifest.assembled_at,
        "authorization_granted": manifest.authorization_granted,
        "bundle_id": manifest.bundle_id,
        "execution_requested": manifest.execution_requested,
        "manifest_id": manifest.manifest_id,
        "provenance_hashes": list(manifest.provenance_hashes),
        "record_count": manifest.record_count,
        "side_effects_permitted": manifest.side_effects_permitted,
        "trust_established": manifest.trust_established,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    manifest = make_manifest()
    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    result = hasher.hash_manifest(manifest)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    manifest = make_manifest()
    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    assert hasher.hash_manifest(manifest) == expected_hash(manifest)


def test_hasher_is_deterministic() -> None:
    manifest = make_manifest()
    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    assert (
        hasher.hash_manifest(manifest)
        == hasher.hash_manifest(manifest)
    )


def test_equivalent_manifests_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    assert (
        hasher.hash_manifest(make_manifest())
        == hasher.hash_manifest(make_manifest())
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("manifest_id", "HAEPM-000002"),
        ("bundle_id", "HSAB-000002"),
        (
            "provenance_hashes",
            (
                "a" * 64,
                "c" * 64,
            ),
        ),
        ("record_count", 1),
        ("assembled_at", "2026-07-16T19:01:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: object,
) -> None:
    baseline = make_manifest()

    values = {
        "manifest_id": baseline.manifest_id,
        "bundle_id": baseline.bundle_id,
        "provenance_hashes": baseline.provenance_hashes,
        "record_count": baseline.record_count,
        "assembled_at": baseline.assembled_at,
    }

    if field_name == "record_count":
        values["provenance_hashes"] = ("a" * 64,)

    values[field_name] = changed_value

    changed = make_manifest(**values)

    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    assert (
        hasher.hash_manifest(baseline)
        != hasher.hash_manifest(changed)
    )


def test_provenance_hash_order_changes_manifest_hash() -> None:
    baseline = make_manifest()

    reordered = make_manifest(
        provenance_hashes=(
            "b" * 64,
            "a" * 64,
        ),
    )

    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    assert (
        hasher.hash_manifest(baseline)
        != hasher.hash_manifest(reordered)
    )


def test_hasher_rejects_none_manifest() -> None:
    hasher = HistoricalAdmissibilityEvidenceProvenanceManifestHasher()

    with pytest.raises(ValueError):
        hasher.hash_manifest(None)


def test_hasher_does_not_mutate_manifest() -> None:
    manifest = make_manifest()
    original = manifest

    HistoricalAdmissibilityEvidenceProvenanceManifestHasher().hash_manifest(
        manifest
    )

    assert manifest == original
    assert manifest.trust_established is False
    assert manifest.authorization_granted is False
    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False