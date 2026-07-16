import pytest

from models.historical_admissibility_evidence_trust_assessment import (
    HistoricalAdmissibilityEvidenceTrustAssessment,
)
from services.historical_admissibility_evidence_trust_assessment_hasher import (
    HistoricalAdmissibilityEvidenceTrustAssessmentHasher,
)
from services.historical_admissibility_evidence_trust_assessment_validator import (
    HistoricalAdmissibilityEvidenceTrustAssessmentValidator,
)


def make_assessment(
    *,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
    rationale: str = (
        "Source integrity is verified, but institutional trust "
        "remains unproven."
    ),
) -> HistoricalAdmissibilityEvidenceTrustAssessment:
    return HistoricalAdmissibilityEvidenceTrustAssessment(
        assessment_id="HAETA-000001",
        manifest_id="HAEPM-000001",
        manifest_hash="a" * 64,
        trust_status=trust_status,
        confidence_level=confidence_level,
        rationale=rationale,
        policy_version="historical-evidence-trust-v1",
        assessed_at="2026-07-16T20:00:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_assessment_hash() -> None:
    assessment = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
    )

    validator = HistoricalAdmissibilityEvidenceTrustAssessmentValidator()

    assert validator.validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_assessment_hash() -> None:
    validator = HistoricalAdmissibilityEvidenceTrustAssessmentValidator()

    assert validator.validate(
        assessment=make_assessment(),
        expected_hash="b" * 64,
    ) is False


def test_validator_detects_modified_assessment() -> None:
    original = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(original)
    )

    modified = make_assessment(
        trust_status="PASS",
        confidence_level="HIGH",
    )

    validator = HistoricalAdmissibilityEvidenceTrustAssessmentValidator()

    assert validator.validate(
        assessment=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "trust_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_trust_statuses(
    trust_status: str,
) -> None:
    assessment = make_assessment(
        trust_status=trust_status,
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
    )

    assert HistoricalAdmissibilityEvidenceTrustAssessmentValidator().validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_assessment() -> None:
    validator = HistoricalAdmissibilityEvidenceTrustAssessmentValidator()

    with pytest.raises(ValueError):
        validator.validate(
            assessment=None,
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
    validator = HistoricalAdmissibilityEvidenceTrustAssessmentValidator()

    with pytest.raises(ValueError):
        validator.validate(
            assessment=make_assessment(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    assessment = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
        .upper()
    )

    assert HistoricalAdmissibilityEvidenceTrustAssessmentValidator().validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment

    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
    )

    HistoricalAdmissibilityEvidenceTrustAssessmentValidator().validate(
        assessment=assessment,
        expected_hash=expected_hash,
    )

    assert assessment == original
    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_successful_validation_does_not_establish_trust() -> None:
    assessment = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
    )

    validator = HistoricalAdmissibilityEvidenceTrustAssessmentValidator()

    assert validator.validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True

    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False