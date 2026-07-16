from dataclasses import FrozenInstanceError

import pytest

from models.historical_admissibility_evidence_admission_assessment import (
    HistoricalAdmissibilityEvidenceAdmissionAssessment,
)


def make_assessment(
    *,
    admission_status: str = "HOLD",
) -> HistoricalAdmissibilityEvidenceAdmissionAssessment:
    return HistoricalAdmissibilityEvidenceAdmissionAssessment(
        assessment_id="HAEAA-000001",
        trust_receipt_id="HAETR-000001",
        trust_receipt_hash="a" * 64,
        admission_status=admission_status,
        rationale=(
            "Trust evidence is recorded, but governance admission "
            "criteria remain incomplete."
        ),
        policy_version="historical-evidence-admission-v1",
        assessed_at="2026-07-16T21:00:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_assessment_records_evidence_admission_result() -> None:
    assessment = make_assessment()

    assert assessment.assessment_id == "HAEAA-000001"
    assert assessment.trust_receipt_id == "HAETR-000001"
    assert assessment.trust_receipt_hash == "a" * 64
    assert assessment.admission_status == "HOLD"
    assert assessment.rationale
    assert assessment.policy_version == "historical-evidence-admission-v1"
    assert assessment.assessed_at == "2026-07-16T21:00:00Z"


def test_assessment_is_immutable() -> None:
    assessment = make_assessment()

    with pytest.raises(FrozenInstanceError):
        assessment.admission_status = "PASS"  # type: ignore[misc]


@pytest.mark.parametrize(
    "admission_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_assessment_supports_admission_statuses(
    admission_status: str,
) -> None:
    assessment = make_assessment(
        admission_status=admission_status,
    )

    assert assessment.admission_status == admission_status


@pytest.mark.parametrize(
    "field_name",
    [
        "assessment_id",
        "trust_receipt_id",
        "trust_receipt_hash",
        "admission_status",
        "rationale",
        "policy_version",
        "assessed_at",
    ],
)
def test_assessment_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "assessment_id": "HAEAA-000001",
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "a" * 64,
        "admission_status": "HOLD",
        "rationale": (
            "Trust evidence is recorded, but governance admission "
            "criteria remain incomplete."
        ),
        "policy_version": "historical-evidence-admission-v1",
        "assessed_at": "2026-07-16T21:00:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceAdmissionAssessment(**values)


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_assessment_rejects_invalid_trust_receipt_hash(
    invalid_hash: str,
) -> None:
    values = {
        "assessment_id": "HAEAA-000001",
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": invalid_hash,
        "admission_status": "HOLD",
        "rationale": "Admission evidence remains incomplete.",
        "policy_version": "historical-evidence-admission-v1",
        "assessed_at": "2026-07-16T21:00:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceAdmissionAssessment(**values)


def test_assessment_rejects_unknown_admission_status() -> None:
    with pytest.raises(ValueError):
        make_assessment(
            admission_status="UNKNOWN",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "evidence_admitted",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    ],
)
def test_assessment_rejects_admission_authority_or_execution_flags(
    field_name: str,
) -> None:
    values = {
        "assessment_id": "HAEAA-000001",
        "trust_receipt_id": "HAETR-000001",
        "trust_receipt_hash": "a" * 64,
        "admission_status": "HOLD",
        "rationale": "Admission assessment remains observer-only.",
        "policy_version": "historical-evidence-admission-v1",
        "assessed_at": "2026-07-16T21:00:00Z",
        "evidence_admitted": False,
        "authorization_granted": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    values[field_name] = True

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidenceAdmissionAssessment(**values)


def test_assessment_preserves_observer_only_invariants() -> None:
    assessment = make_assessment(
        admission_status="PASS",
    )

    assert assessment.admission_status == "PASS"
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False