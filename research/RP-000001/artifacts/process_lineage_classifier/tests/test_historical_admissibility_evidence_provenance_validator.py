import pytest

from models.historical_admissibility_evidence_provenance import (
    HistoricalAdmissibilityEvidenceProvenance,
)
from services.historical_admissibility_evidence_provenance_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceHasher,
)
from services.historical_admissibility_evidence_provenance_validator import (
    HistoricalAdmissibilityEvidenceProvenanceValidator,
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


def test_validator_accepts_matching_provenance_hash() -> None:
    provenance = make_provenance()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceHasher()
        .hash_provenance(provenance)
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    assert validator.validate(
        provenance=provenance,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_provenance_hash() -> None:
    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    assert validator.validate(
        provenance=make_provenance(),
        expected_hash="b" * 64,
    ) is False


def test_validator_detects_modified_provenance() -> None:
    original = make_provenance()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceHasher()
        .hash_provenance(original)
    )

    modified = make_provenance(
        source_system="modified-registry",
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    assert validator.validate(
        provenance=modified,
        expected_hash=expected_hash,
    ) is False


def test_validator_rejects_none_provenance() -> None:
    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    with pytest.raises(ValueError):
        validator.validate(
            provenance=None,
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
    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    with pytest.raises(ValueError):
        validator.validate(
            provenance=make_provenance(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    provenance = make_provenance()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceHasher()
        .hash_provenance(provenance)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    assert validator.validate(
        provenance=provenance,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_provenance() -> None:
    provenance = make_provenance()
    original = provenance

    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceHasher()
        .hash_provenance(provenance)
    )

    HistoricalAdmissibilityEvidenceProvenanceValidator().validate(
        provenance=provenance,
        expected_hash=expected_hash,
    )

    assert provenance == original
    assert provenance.trust_established is False
    assert provenance.authorization_granted is False
    assert provenance.execution_requested is False
    assert provenance.side_effects_permitted is False


def test_successful_validation_does_not_establish_trust() -> None:
    provenance = make_provenance()
    expected_hash = (
        HistoricalAdmissibilityEvidenceProvenanceHasher()
        .hash_provenance(provenance)
    )

    validator = HistoricalAdmissibilityEvidenceProvenanceValidator()

    assert validator.validate(
        provenance=provenance,
        expected_hash=expected_hash,
    ) is True

    assert provenance.trust_established is False
    assert provenance.authorization_granted is False
    assert provenance.execution_requested is False
    assert provenance.side_effects_permitted is False