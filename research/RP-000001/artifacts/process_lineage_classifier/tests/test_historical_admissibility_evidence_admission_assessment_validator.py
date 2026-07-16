import pytest

from models.historical_admissibility_evidence_admission_assessment import (
    HistoricalAdmissibilityEvidenceAdmissionAssessment,
)
from services.historical_admissibility_evidence_admission_assessment_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher,
)
from services.historical_admissibility_evidence_admission_assessment_validator import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator,
)


def make_assessment(
    *,
    admission_status: str = "HOLD",
    rationale: str = (
        "Trust evidence is recorded, but governance admission "
        "criteria remain incomplete."
    ),
) -> HistoricalAdmissibilityEvidenceAdmissionAssessment:
    return HistoricalAdmissibilityEvidenceAdmissionAssessment(
        assessment_id="HAEAA-000001",
        trust_receipt_id="HAETR-000001",
        trust_receipt_hash="a" * 64,
        admission_status=admission_status,
        rationale=rationale,
        policy_version="historical-evidence-admission-v1",
        assessed_at="2026-07-16T21:00:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_assessment_hash() -> None:
    assessment = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    assert validator.validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_assessment_hash() -> None:
    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    assert validator.validate(
        assessment=make_assessment(),
        expected_hash="b" * 64,
    ) is False


def test_validator_detects_modified_assessment() -> None:
    original = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(original)
    )

    modified = make_assessment(
        admission_status="PASS",
        rationale="Admission criteria are satisfied.",
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    assert validator.validate(
        assessment=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "admission_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_admission_statuses(
    admission_status: str,
) -> None:
    assessment = make_assessment(
        admission_status=admission_status,
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    assert validator.validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_assessment() -> None:
    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

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
    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    with pytest.raises(ValueError):
        validator.validate(
            assessment=make_assessment(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    assessment = make_assessment()
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
        .upper()
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    assert validator.validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment

    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
    )

    HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator().validate(
        assessment=assessment,
        expected_hash=expected_hash,
    )

    assert assessment == original
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_successful_validation_does_not_admit_evidence() -> None:
    assessment = make_assessment(
        admission_status="PASS",
    )
    expected_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
    )

    validator = HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()

    assert validator.validate(
        assessment=assessment,
        expected_hash=expected_hash,
    ) is True

    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False