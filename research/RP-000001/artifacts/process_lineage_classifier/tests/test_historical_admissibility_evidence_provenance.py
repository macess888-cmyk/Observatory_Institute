from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_provenance import (
    HistoricalAdmissibilityEvidenceProvenance,
)


def make_provenance() -> HistoricalAdmissibilityEvidenceProvenance:
    return HistoricalAdmissibilityEvidenceProvenance(
        provenance_id="HAEP-000001",
        bundle_id="HSAB-000001",
        evidence_id="EVD-000001",
        evidence_type="KEY_COMPROMISE_EVENT",
        source_system="historical-key-registry",
        source_reference="registry://keys/KEY-000001/events/KCE-000001",
        source_hash="a" * 64,
        observed_at="2026-07-16T18:30:00Z",
        collected_at="2026-07-16T18:35:00Z",
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_provenance_records_evidence_origin() -> None:
    provenance = make_provenance()

    assert provenance.provenance_id == "HAEP-000001"
    assert provenance.bundle_id == "HSAB-000001"
    assert provenance.evidence_id == "EVD-000001"
    assert provenance.evidence_type == "KEY_COMPROMISE_EVENT"
    assert provenance.source_system == "historical-key-registry"
    assert (
        provenance.source_reference
        == "registry://keys/KEY-000001/events/KCE-000001"
    )
    assert provenance.source_hash == "a" * 64
    assert provenance.observed_at == "2026-07-16T18:30:00Z"
    assert provenance.collected_at == "2026-07-16T18:35:00Z"


def test_provenance_is_immutable() -> None:
    provenance = make_provenance()

    with pytest.raises(FrozenInstanceError):
        provenance.source_system = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "provenance_id",
        "bundle_id",
        "evidence_id",
        "evidence_type",
        "source_system",
        "source_reference",
        "source_hash",
        "observed_at",
        "collected_at",
    ],
)
def test_provenance_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "provenance_id": "HAEP-000001",
        "bundle_id": "HSAB-000001",
        "evidence_id": "EVD-000001",
        "evidence_type": "KEY_COMPROMISE_EVENT",
        "source_system": "historical-key-registry",
        "source_reference": (
            "registry://keys/KEY-000001/events/KCE-000001"
        ),
        "source_hash": "a" * 64,
        "observed_at": "2026-07-16T18:30:00Z",
        "collected_at": "2026-07-16T18:35:00Z",
        "trust_established": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenance(**values)


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_provenance_rejects_invalid_source_hash(
    invalid_hash: str,
) -> None:
    values = {
        "provenance_id": "HAEP-000001",
        "bundle_id": "HSAB-000001",
        "evidence_id": "EVD-000001",
        "evidence_type": "KEY_COMPROMISE_EVENT",
        "source_system": "historical-key-registry",
        "source_reference": (
            "registry://keys/KEY-000001/events/KCE-000001"
        ),
        "source_hash": invalid_hash,
        "observed_at": "2026-07-16T18:30:00Z",
        "collected_at": "2026-07-16T18:35:00Z",
        "trust_established": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenance(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "trust_established",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_provenance_rejects_trust_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "provenance_id": "HAEP-000001",
        "bundle_id": "HSAB-000001",
        "evidence_id": "EVD-000001",
        "evidence_type": "KEY_COMPROMISE_EVENT",
        "source_system": "historical-key-registry",
        "source_reference": (
            "registry://keys/KEY-000001/events/KCE-000001"
        ),
        "source_hash": "a" * 64,
        "observed_at": "2026-07-16T18:30:00Z",
        "collected_at": "2026-07-16T18:35:00Z",
        "trust_established": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenance(**values)


def test_provenance_preserves_observer_only_invariants() -> None:
    provenance = make_provenance()

    assert provenance.trust_established is False
    assert provenance.authorization_granted is False
    assert provenance.execution_requested is False
    assert provenance.side_effects_permitted is False