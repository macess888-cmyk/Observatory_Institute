from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_trust_assessment import (
    HistoricalAdmissibilityEvidenceTrustAssessment,
)


def make_assessment(
    *,
    trust_status: str = "HOLD",
) -> HistoricalAdmissibilityEvidenceTrustAssessment:
    return HistoricalAdmissibilityEvidenceTrustAssessment(
        assessment_id="HAETA-000001",
        manifest_id="HAEPM-000001",
        manifest_hash="a" * 64,
        trust_status=trust_status,
        confidence_level="MEDIUM",
        rationale="Source integrity is verified, but institutional trust remains unproven.",
        policy_version="historical-evidence-trust-v1",
        assessed_at="2026-07-16T20:00:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_assessment_records_historical_evidence_trust_result() -> None:
    assessment = make_assessment()

    assert assessment.assessment_id == "HAETA-000001"
    assert assessment.manifest_id == "HAEPM-000001"
    assert assessment.manifest_hash == "a" * 64
    assert assessment.trust_status == "HOLD"
    assert assessment.confidence_level == "MEDIUM"
    assert assessment.rationale
    assert assessment.policy_version == "historical-evidence-trust-v1"
    assert assessment.assessed_at == "2026-07-16T20:00:00Z"


def test_assessment_is_immutable() -> None:
    assessment = make_assessment()

    with pytest.raises(FrozenInstanceError):
        assessment.trust_status = "PASS"  # type: ignore[misc]


@pytest.mark.parametrize(
    "trust_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_assessment_supports_trust_statuses(
    trust_status: str,
) -> None:
    assessment = make_assessment(
        trust_status=trust_status,
    )

    assert assessment.trust_status == trust_status


@pytest.mark.parametrize(
    "confidence_level",
    ["LOW", "MEDIUM", "HIGH"],
)
def test_assessment_supports_confidence_levels(
    confidence_level: str,
) -> None:
    assessment = HistoricalAdmissibilityEvidenceTrustAssessment(
        assessment_id="HAETA-000001",
        manifest_id="HAEPM-000001",
        manifest_hash="a" * 64,
        trust_status="HOLD",
        confidence_level=confidence_level,
        rationale="Evidence remains under observer-only trust assessment.",
        policy_version="historical-evidence-trust-v1",
        assessed_at="2026-07-16T20:00:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    assert assessment.confidence_level == confidence_level


@pytest.mark.parametrize(
    "field_name",
    [
        "assessment_id",
        "manifest_id",
        "manifest_hash",
        "trust_status",
        "confidence_level",
        "rationale",
        "policy_version",
        "assessed_at",
    ],
)
def test_assessment_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "assessment_id": "HAETA-000001",
        "manifest_id": "HAEPM-000001",
        "manifest_hash": "a" * 64,
        "trust_status": "HOLD",
        "confidence_level": "MEDIUM",
        "rationale": (
            "Source integrity is verified, but institutional trust "
            "remains unproven."
        ),
        "policy_version": "historical-evidence-trust-v1",
        "assessed_at": "2026-07-16T20:00:00Z",
        "trust_established": False,
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustAssessment(**values)


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_assessment_rejects_invalid_manifest_hash(
    invalid_hash: str,
) -> None:
    values = {
        "assessment_id": "HAETA-000001",
        "manifest_id": "HAEPM-000001",
        "manifest_hash": invalid_hash,
        "trust_status": "HOLD",
        "confidence_level": "MEDIUM",
        "rationale": "Manifest trust remains unproven.",
        "policy_version": "historical-evidence-trust-v1",
        "assessed_at": "2026-07-16T20:00:00Z",
        "trust_established": False,
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustAssessment(**values)


def test_assessment_rejects_unknown_trust_status() -> None:
    with pytest.raises(ValueError):
        make_assessment(
            trust_status="UNKNOWN",
        )


def test_assessment_rejects_unknown_confidence_level() -> None:
    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustAssessment(
            assessment_id="HAETA-000001",
            manifest_id="HAEPM-000001",
            manifest_hash="a" * 64,
            trust_status="HOLD",
            confidence_level="CERTAIN",
            rationale="Unsupported confidence level.",
            policy_version="historical-evidence-trust-v1",
            assessed_at="2026-07-16T20:00:00Z",
            trust_established=False,
            evidence_admitted=False,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "trust_established",
        "evidence_admitted",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_assessment_rejects_trust_admission_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "assessment_id": "HAETA-000001",
        "manifest_id": "HAEPM-000001",
        "manifest_hash": "a" * 64,
        "trust_status": "HOLD",
        "confidence_level": "MEDIUM",
        "rationale": "Trust assessment remains observer-only.",
        "policy_version": "historical-evidence-trust-v1",
        "assessed_at": "2026-07-16T20:00:00Z",
        "trust_established": False,
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceTrustAssessment(**values)


def test_assessment_preserves_observer_only_invariants() -> None:
    assessment = make_assessment()

    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False