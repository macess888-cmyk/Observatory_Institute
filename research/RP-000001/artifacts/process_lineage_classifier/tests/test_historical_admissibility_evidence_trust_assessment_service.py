import pytest

from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)
from models.historical_admissibility_evidence_trust_assessment import (
    HistoricalAdmissibilityEvidenceTrustAssessment,
)
from services.historical_admissibility_evidence_provenance_manifest_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceManifestHasher,
)
from services.historical_admissibility_evidence_trust_assessment_service import (
    HistoricalAdmissibilityEvidenceTrustAssessmentService,
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


def create_assessment(
    *,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
) -> HistoricalAdmissibilityEvidenceTrustAssessment:
    manifest = make_manifest()
    manifest_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
    )

    return HistoricalAdmissibilityEvidenceTrustAssessmentService().assess(
        assessment_id="HAETA-000001",
        manifest=manifest,
        manifest_hash=manifest_hash,
        trust_status=trust_status,
        confidence_level=confidence_level,
        rationale=(
            "Source integrity is verified, but institutional trust "
            "remains unproven."
        ),
        policy_version="historical-evidence-trust-v1",
        assessed_at="2026-07-16T20:00:00Z",
    )


def test_service_creates_assessment_from_validated_manifest() -> None:
    assessment = create_assessment()

    assert isinstance(
        assessment,
        HistoricalAdmissibilityEvidenceTrustAssessment,
    )
    assert assessment.assessment_id == "HAETA-000001"
    assert assessment.manifest_id == "HAEPM-000001"
    assert assessment.trust_status == "HOLD"
    assert assessment.confidence_level == "MEDIUM"
    assert assessment.policy_version == "historical-evidence-trust-v1"
    assert assessment.assessed_at == "2026-07-16T20:00:00Z"


@pytest.mark.parametrize(
    "trust_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_supports_all_trust_statuses(
    trust_status: str,
) -> None:
    assessment = create_assessment(
        trust_status=trust_status,
    )

    assert assessment.trust_status == trust_status


@pytest.mark.parametrize(
    "confidence_level",
    ["LOW", "MEDIUM", "HIGH"],
)
def test_service_supports_all_confidence_levels(
    confidence_level: str,
) -> None:
    assessment = create_assessment(
        confidence_level=confidence_level,
    )

    assert assessment.confidence_level == confidence_level


def test_service_rejects_none_manifest() -> None:
    service = HistoricalAdmissibilityEvidenceTrustAssessmentService()

    with pytest.raises(ValueError):
        service.assess(
            assessment_id="HAETA-000001",
            manifest=None,
            manifest_hash="a" * 64,
            trust_status="HOLD",
            confidence_level="MEDIUM",
            rationale="Manifest is missing.",
            policy_version="historical-evidence-trust-v1",
            assessed_at="2026-07-16T20:00:00Z",
        )


def test_service_rejects_non_matching_manifest_hash() -> None:
    service = HistoricalAdmissibilityEvidenceTrustAssessmentService()

    with pytest.raises(ValueError):
        service.assess(
            assessment_id="HAETA-000001",
            manifest=make_manifest(),
            manifest_hash="c" * 64,
            trust_status="HOLD",
            confidence_level="MEDIUM",
            rationale="Manifest integrity could not be confirmed.",
            policy_version="historical-evidence-trust-v1",
            assessed_at="2026-07-16T20:00:00Z",
        )


@pytest.mark.parametrize(
    "manifest_hash",
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
def test_service_rejects_invalid_manifest_hash(
    manifest_hash: str | None,
) -> None:
    service = HistoricalAdmissibilityEvidenceTrustAssessmentService()

    with pytest.raises(ValueError):
        service.assess(
            assessment_id="HAETA-000001",
            manifest=make_manifest(),
            manifest_hash=manifest_hash,
            trust_status="HOLD",
            confidence_level="MEDIUM",
            rationale="Manifest hash is invalid.",
            policy_version="historical-evidence-trust-v1",
            assessed_at="2026-07-16T20:00:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    assessment = create_assessment()

    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_service_does_not_mutate_manifest() -> None:
    manifest = make_manifest()
    original = manifest
    manifest_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
    )

    HistoricalAdmissibilityEvidenceTrustAssessmentService().assess(
        assessment_id="HAETA-000001",
        manifest=manifest,
        manifest_hash=manifest_hash,
        trust_status="HOLD",
        confidence_level="MEDIUM",
        rationale="Trust remains under assessment.",
        policy_version="historical-evidence-trust-v1",
        assessed_at="2026-07-16T20:00:00Z",
    )

    assert manifest == original
    assert manifest.trust_established is False
    assert manifest.authorization_granted is False
    assert manifest.execution_requested is False
    assert manifest.side_effects_permitted is False


def test_pass_assessment_does_not_establish_trust() -> None:
    assessment = create_assessment(
        trust_status="PASS",
        confidence_level="HIGH",
    )

    assert assessment.trust_status == "PASS"
    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False