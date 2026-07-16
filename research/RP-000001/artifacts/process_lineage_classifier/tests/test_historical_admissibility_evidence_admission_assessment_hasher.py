import hashlib
import json

import pytest

from models.historical_admissibility_evidence_admission_assessment import (
    HistoricalAdmissibilityEvidenceAdmissionAssessment,
)
from services.historical_admissibility_evidence_admission_assessment_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher,
)


def make_assessment(
    *,
    assessment_id: str = "HAEAA-000001",
    trust_receipt_id: str = "HAETR-000001",
    trust_receipt_hash: str = "a" * 64,
    admission_status: str = "HOLD",
    rationale: str = (
        "Trust evidence is recorded, but governance admission "
        "criteria remain incomplete."
    ),
    policy_version: str = "historical-evidence-admission-v1",
    assessed_at: str = "2026-07-16T21:00:00Z",
) -> HistoricalAdmissibilityEvidenceAdmissionAssessment:
    return HistoricalAdmissibilityEvidenceAdmissionAssessment(
        assessment_id=assessment_id,
        trust_receipt_id=trust_receipt_id,
        trust_receipt_hash=trust_receipt_hash,
        admission_status=admission_status,
        rationale=rationale,
        policy_version=policy_version,
        assessed_at=assessed_at,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def expected_hash(
    assessment: HistoricalAdmissibilityEvidenceAdmissionAssessment,
) -> str:
    payload = {
        "admission_status": assessment.admission_status,
        "assessed_at": assessment.assessed_at,
        "assessment_id": assessment.assessment_id,
        "authorization_granted": assessment.authorization_granted,
        "evidence_admitted": assessment.evidence_admitted,
        "execution_requested": assessment.execution_requested,
        "policy_version": assessment.policy_version,
        "rationale": assessment.rationale,
        "side_effects_permitted": assessment.side_effects_permitted,
        "trust_receipt_hash": assessment.trust_receipt_hash,
        "trust_receipt_id": assessment.trust_receipt_id,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def test_hasher_returns_sha256_hex_digest() -> None:
    assessment = make_assessment()
    hasher = HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()

    result = hasher.hash_assessment(assessment)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_hasher_matches_canonical_expected_hash() -> None:
    assessment = make_assessment()

    assert (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
        == expected_hash(assessment)
    )


def test_hasher_is_deterministic() -> None:
    assessment = make_assessment()
    hasher = HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()

    assert (
        hasher.hash_assessment(assessment)
        == hasher.hash_assessment(assessment)
    )


def test_equivalent_assessments_produce_same_hash() -> None:
    hasher = HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()

    assert (
        hasher.hash_assessment(make_assessment())
        == hasher.hash_assessment(make_assessment())
    )


@pytest.mark.parametrize(
    "field_name, changed_value",
    [
        ("assessment_id", "HAEAA-000002"),
        ("trust_receipt_id", "HAETR-000002"),
        ("trust_receipt_hash", "b" * 64),
        ("admission_status", "PASS"),
        ("rationale", "Admission criteria are satisfied."),
        ("policy_version", "historical-evidence-admission-v2"),
        ("assessed_at", "2026-07-16T21:01:00Z"),
    ],
)
def test_material_field_changes_change_hash(
    field_name: str,
    changed_value: str,
) -> None:
    baseline = make_assessment()

    values = {
        "assessment_id": baseline.assessment_id,
        "trust_receipt_id": baseline.trust_receipt_id,
        "trust_receipt_hash": baseline.trust_receipt_hash,
        "admission_status": baseline.admission_status,
        "rationale": baseline.rationale,
        "policy_version": baseline.policy_version,
        "assessed_at": baseline.assessed_at,
    }
    values[field_name] = changed_value

    changed = make_assessment(**values)

    hasher = HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()

    assert (
        hasher.hash_assessment(baseline)
        != hasher.hash_assessment(changed)
    )


def test_hasher_rejects_none_assessment() -> None:
    hasher = HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()

    with pytest.raises(ValueError):
        hasher.hash_assessment(None)


def test_hasher_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment

    HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher().hash_assessment(
        assessment
    )

    assert assessment == original
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False