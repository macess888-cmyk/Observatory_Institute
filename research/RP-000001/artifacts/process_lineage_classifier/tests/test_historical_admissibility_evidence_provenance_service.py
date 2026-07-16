import pytest

from models.historical_admissibility_evidence_provenance import (
    HistoricalAdmissibilityEvidenceProvenance,
)
from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)
from services.historical_admissibility_evidence_provenance_service import (
    HistoricalAdmissibilityEvidenceProvenanceService,
)


def make_bundle() -> HistoricalSignatureAdmissibilityBundle:
    return HistoricalSignatureAdmissibilityBundle(
        bundle_id="HSAB-000001",
        receipt_id="HSAR-000001",
        receipt_hash="a" * 64,
        assessment_hash="b" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status="PASS",
        policy_version="historical-signature-admissibility-v1",
        exported_at="2026-07-16T18:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_creates_provenance_for_bundle_evidence() -> None:
    bundle = make_bundle()
    service = HistoricalAdmissibilityEvidenceProvenanceService()

    provenance = service.create_provenance(
        provenance_id="HAEP-000001",
        bundle=bundle,
        evidence_id="EVD-000001",
        evidence_type="KEY_COMPROMISE_EVENT",
        source_system="historical-key-registry",
        source_reference=(
            "registry://keys/KEY-000001/events/KCE-000001"
        ),
        source_hash="c" * 64,
        observed_at="2026-07-16T18:30:00Z",
        collected_at="2026-07-16T18:35:00Z",
    )

    assert isinstance(
        provenance,
        HistoricalAdmissibilityEvidenceProvenance,
    )
    assert provenance.provenance_id == "HAEP-000001"
    assert provenance.bundle_id == bundle.bundle_id
    assert provenance.evidence_id == "EVD-000001"
    assert provenance.evidence_type == "KEY_COMPROMISE_EVENT"
    assert provenance.source_system == "historical-key-registry"
    assert (
        provenance.source_reference
        == "registry://keys/KEY-000001/events/KCE-000001"
    )
    assert provenance.source_hash == "c" * 64
    assert provenance.observed_at == "2026-07-16T18:30:00Z"
    assert provenance.collected_at == "2026-07-16T18:35:00Z"


def test_service_binds_provenance_to_supplied_bundle() -> None:
    bundle = make_bundle()

    provenance = (
        HistoricalAdmissibilityEvidenceProvenanceService()
        .create_provenance(
            provenance_id="HAEP-000001",
            bundle=bundle,
            evidence_id="EVD-000001",
            evidence_type="KEY_COMPROMISE_EVENT",
            source_system="historical-key-registry",
            source_reference=(
                "registry://keys/KEY-000001/events/KCE-000001"
            ),
            source_hash="c" * 64,
            observed_at="2026-07-16T18:30:00Z",
            collected_at="2026-07-16T18:35:00Z",
        )
    )

    assert provenance.bundle_id == bundle.bundle_id


def test_service_rejects_none_bundle() -> None:
    service = HistoricalAdmissibilityEvidenceProvenanceService()

    with pytest.raises(ValueError):
        service.create_provenance(
            provenance_id="HAEP-000001",
            bundle=None,
            evidence_id="EVD-000001",
            evidence_type="KEY_COMPROMISE_EVENT",
            source_system="historical-key-registry",
            source_reference=(
                "registry://keys/KEY-000001/events/KCE-000001"
            ),
            source_hash="c" * 64,
            observed_at="2026-07-16T18:30:00Z",
            collected_at="2026-07-16T18:35:00Z",
        )


def test_service_rejects_bundle_without_bundle_id() -> None:
    class BundleWithoutIdentifier:
        pass

    service = HistoricalAdmissibilityEvidenceProvenanceService()

    with pytest.raises(ValueError):
        service.create_provenance(
            provenance_id="HAEP-000001",
            bundle=BundleWithoutIdentifier(),
            evidence_id="EVD-000001",
            evidence_type="KEY_COMPROMISE_EVENT",
            source_system="historical-key-registry",
            source_reference=(
                "registry://keys/KEY-000001/events/KCE-000001"
            ),
            source_hash="c" * 64,
            observed_at="2026-07-16T18:30:00Z",
            collected_at="2026-07-16T18:35:00Z",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "provenance_id",
        "evidence_id",
        "evidence_type",
        "source_system",
        "source_reference",
        "source_hash",
        "observed_at",
        "collected_at",
    ],
)
def test_service_rejects_empty_required_values(
    field_name: str,
) -> None:
    values = {
        "provenance_id": "HAEP-000001",
        "bundle": make_bundle(),
        "evidence_id": "EVD-000001",
        "evidence_type": "KEY_COMPROMISE_EVENT",
        "source_system": "historical-key-registry",
        "source_reference": (
            "registry://keys/KEY-000001/events/KCE-000001"
        ),
        "source_hash": "c" * 64,
        "observed_at": "2026-07-16T18:30:00Z",
        "collected_at": "2026-07-16T18:35:00Z",
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceProvenanceService().create_provenance(
            **values
        )


def test_service_preserves_observer_only_invariants() -> None:
    provenance = (
        HistoricalAdmissibilityEvidenceProvenanceService()
        .create_provenance(
            provenance_id="HAEP-000001",
            bundle=make_bundle(),
            evidence_id="EVD-000001",
            evidence_type="KEY_COMPROMISE_EVENT",
            source_system="historical-key-registry",
            source_reference=(
                "registry://keys/KEY-000001/events/KCE-000001"
            ),
            source_hash="c" * 64,
            observed_at="2026-07-16T18:30:00Z",
            collected_at="2026-07-16T18:35:00Z",
        )
    )

    assert provenance.trust_established is False
    assert provenance.authorization_granted is False
    assert provenance.execution_requested is False
    assert provenance.side_effects_permitted is False


def test_service_does_not_mutate_bundle() -> None:
    bundle = make_bundle()
    original = bundle

    HistoricalAdmissibilityEvidenceProvenanceService().create_provenance(
        provenance_id="HAEP-000001",
        bundle=bundle,
        evidence_id="EVD-000001",
        evidence_type="KEY_COMPROMISE_EVENT",
        source_system="historical-key-registry",
        source_reference=(
            "registry://keys/KEY-000001/events/KCE-000001"
        ),
        source_hash="c" * 64,
        observed_at="2026-07-16T18:30:00Z",
        collected_at="2026-07-16T18:35:00Z",
    )

    assert bundle == original
    assert bundle.authorization_granted is False
    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False


def test_provenance_creation_does_not_establish_source_trust() -> None:
    provenance = (
        HistoricalAdmissibilityEvidenceProvenanceService()
        .create_provenance(
            provenance_id="HAEP-000001",
            bundle=make_bundle(),
            evidence_id="EVD-000001",
            evidence_type="KEY_COMPROMISE_EVENT",
            source_system="historical-key-registry",
            source_reference=(
                "registry://keys/KEY-000001/events/KCE-000001"
            ),
            source_hash="c" * 64,
            observed_at="2026-07-16T18:30:00Z",
            collected_at="2026-07-16T18:35:00Z",
        )
    )

    assert provenance.trust_established is False