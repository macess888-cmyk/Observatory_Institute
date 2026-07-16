import hashlib
import json

import pytest

from models.historical_admissibility_evidence_trust_assessment import (
    HistoricalAdmissibilityEvidenceTrustAssessment,
)
from services.historical_admissibility_evidence_trust_assessment_hasher import (
    HistoricalAdmissibilityEvidenceTrustAssessmentHasher,
)


def make_assessment(
    *,
    assessment_id: str = "HAETA-000001",
    manifest_id: str = "HAEPM-000001",
    manifest_hash: str = "a" * 64,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
    rationale: str = (
        "Source integrity is verified, but institutional trust "
        "remains unproven."
    ),
    policy_version: str = "historical-evidence-trust-v1",
    assessed_at: str = "2026-07-16T20:00:00Z",
) -> HistoricalAdmissibilityEvidenceTrustAssessment:
    return HistoricalAdmissibilityEvidenceTrustAssessment(
        assessment_id=assessment_id,
        manifest_id=manifest_id,
        manifest_hash=manifest_hash,
        trust_status=trust_status,
        confidence_level=confidence_level,
        rationale=rationale,
        policy_version=policy_version,
        assessed_at=assessed_at,
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    assessment: HistoricalAdmissibilityEvidenceTrustAssessment,
) -> str:
    payload = {
        "assessed_at": assessment.assessed_at,
        "assessment_id": assessment.assessment_id,
        "authorization_granted": assessment.authorization_granted,
        "confidence_level": assessment.confidence_level,
        "evidence_admitted": assessment.evidence_admitted,
        "execution_requested": assessment.execution_requested,
        "manifest_hash": assessment.manifest_hash,
        "manifest_id": assessment.manifest_id,
        "policy_version": assessment.policy_version,
        "rationale": assessment.rationale,
        "side_effects_permitted": assessment.side_effects_permitted,
        "trust_established": assessment.trust_established,
        "trust_status": assessment.trust_status,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    assessment = make_assessment()
    hasher = HistoricalAdmissibilityEvidenceTrustAssessmentHasher()

    result = hasher.hash_assessment(assessment)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    assessment = make_assessment()
    hasher = HistoricalAdmissibilityEvidenceTrustAssessmentHasher()

    assert hasher.hash_assessment(assessment) == expected_hash(assessment)


def test_hasher_is_deterministic() -> None:
    assessment = make_assessment()
    hasher = HistoricalAdmissibilityEvidenceTrustAssessmentHasher()

    assert (
        hasher.hash_assessment(assessment)
        == hasher.hash_assessment(assessment)
    )


def test_equivalent_assessments_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidenceTrustAssessmentHasher()

    assert (
        hasher.hash_assessment(make_assessment())
        == hasher.hash_assessment(make_assessment())
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("assessment_id", "HAETA-000002"),
        ("manifest_id", "HAEPM-000002"),
        ("manifest_hash", "b" * 64),
        ("trust_status", "PASS"),
        ("confidence_level", "HIGH"),
        ("rationale", "Independent evidence supports provisional trust."),
        ("policy_version", "historical-evidence-trust-v2"),
        ("assessed_at", "2026-07-16T20:01:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_assessment()

    values = {
        "assessment_id": baseline.assessment_id,
        "manifest_id": baseline.manifest_id,
        "manifest_hash": baseline.manifest_hash,
        "trust_status": baseline.trust_status,
        "confidence_level": baseline.confidence_level,
        "rationale": baseline.rationale,
        "policy_version": baseline.policy_version,
        "assessed_at": baseline.assessed_at,
    }
    values[field_name] = changed_value

    changed = make_assessment(**values)

    hasher = HistoricalAdmissibilityEvidenceTrustAssessmentHasher()

    assert (
        hasher.hash_assessment(baseline)
        != hasher.hash_assessment(changed)
    )


def test_hasher_rejects_none_assessment() -> None:
    hasher = HistoricalAdmissibilityEvidenceTrustAssessmentHasher()

    with pytest.raises(ValueError):
        hasher.hash_assessment(None)


def test_hasher_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment

    HistoricalAdmissibilityEvidenceTrustAssessmentHasher().hash_assessment(
        assessment
    )

    assert assessment == original
    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False