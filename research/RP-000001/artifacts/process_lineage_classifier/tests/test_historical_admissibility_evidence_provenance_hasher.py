import hashlib
import json

import pytest

from models.historical_admissibility_evidence_provenance import (
    HistoricalAdmissibilityEvidenceProvenance,
)
from services.historical_admissibility_evidence_provenance_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceHasher,
)


def make_provenance(
    *,
    provenance_id: str = "HAEP-000001",
    bundle_id: str = "HSAB-000001",
    evidence_id: str = "EVD-000001",
    evidence_type: str = "KEY_COMPROMISE_EVENT",
    source_system: str = "historical-key-registry",
    source_reference: str = (
        "registry://keys/KEY-000001/events/KCE-000001"
    ),
    source_hash: str = "a" * 64,
    observed_at: str = "2026-07-16T18:30:00Z",
    collected_at: str = "2026-07-16T18:35:00Z",
) -> HistoricalAdmissibilityEvidenceProvenance:
    return HistoricalAdmissibilityEvidenceProvenance(
        provenance_id=provenance_id,
        bundle_id=bundle_id,
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        source_system=source_system,
        source_reference=source_reference,
        source_hash=source_hash,
        observed_at=observed_at,
        collected_at=collected_at,
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    provenance: HistoricalAdmissibilityEvidenceProvenance,
) -> str:
    payload = {
        "authorization_granted": provenance.authorization_granted,
        "bundle_id": provenance.bundle_id,
        "collected_at": provenance.collected_at,
        "evidence_id": provenance.evidence_id,
        "evidence_type": provenance.evidence_type,
        "execution_requested": provenance.execution_requested,
        "observed_at": provenance.observed_at,
        "provenance_id": provenance.provenance_id,
        "side_effects_permitted": provenance.side_effects_permitted,
        "source_hash": provenance.source_hash,
        "source_reference": provenance.source_reference,
        "source_system": provenance.source_system,
        "trust_established": provenance.trust_established,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    provenance = make_provenance()
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    result = hasher.hash_provenance(provenance)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    provenance = make_provenance()
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    assert hasher.hash_provenance(provenance) == expected_hash(provenance)


def test_hasher_is_deterministic() -> None:
    provenance = make_provenance()
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    assert (
        hasher.hash_provenance(provenance)
        == hasher.hash_provenance(provenance)
    )


def test_equivalent_provenance_records_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    assert (
        hasher.hash_provenance(make_provenance())
        == hasher.hash_provenance(make_provenance())
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("provenance_id", "HAEP-000002"),
        ("bundle_id", "HSAB-000002"),
        ("evidence_id", "EVD-000002"),
        ("evidence_type", "SIGNATURE_VERIFICATION_RECEIPT"),
        ("source_system", "historical-signature-registry"),
        (
            "source_reference",
            "registry://signatures/SIG-000001/receipts/HSVR-000001",
        ),
        ("source_hash", "b" * 64),
        ("observed_at", "2026-07-16T18:31:00Z"),
        ("collected_at", "2026-07-16T18:36:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_provenance()

    values = {
        "provenance_id": baseline.provenance_id,
        "bundle_id": baseline.bundle_id,
        "evidence_id": baseline.evidence_id,
        "evidence_type": baseline.evidence_type,
        "source_system": baseline.source_system,
        "source_reference": baseline.source_reference,
        "source_hash": baseline.source_hash,
        "observed_at": baseline.observed_at,
        "collected_at": baseline.collected_at,
    }
    values[field_name] = changed_value

    changed = make_provenance(**values)

    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    assert (
        hasher.hash_provenance(baseline)
        != hasher.hash_provenance(changed)
    )


def test_hasher_rejects_none_provenance() -> None:
    hasher = HistoricalAdmissibilityEvidenceProvenanceHasher()

    with pytest.raises(ValueError):
        hasher.hash_provenance(None)


def test_hasher_does_not_mutate_provenance() -> None:
    provenance = make_provenance()
    original = provenance

    HistoricalAdmissibilityEvidenceProvenanceHasher().hash_provenance(
        provenance
    )

    assert provenance == original
    assert provenance.trust_established is False
    assert provenance.authorization_granted is False
    assert provenance.execution_requested is False
    assert provenance.side_effects_permitted is False