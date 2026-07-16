import pytest

from models.historical_admissibility_evidence_admission_assessment import (
    HistoricalAdmissibilityEvidenceAdmissionAssessment,
)
from models.historical_admissibility_evidence_admission_receipt import (
    HistoricalAdmissibilityEvidenceAdmissionReceipt,
)
from services.historical_admissibility_evidence_admission_assessment_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher,
)
from services.historical_admissibility_evidence_admission_receipt_service import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptService,
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


def create_receipt(
    *,
    admission_status: str = "HOLD",
) -> HistoricalAdmissibilityEvidenceAdmissionReceipt:
    assessment = make_assessment(
        admission_status=admission_status,
    )
    assessment_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
    )

    return HistoricalAdmissibilityEvidenceAdmissionReceiptService().create_receipt(
        receipt_id="HAEAR-000001",
        assessment=assessment,
        assessment_hash=assessment_hash,
        recorded_at="2026-07-16T21:30:00Z",
    )


def test_service_creates_receipt_from_validated_assessment() -> None:
    receipt = create_receipt()

    assert isinstance(
        receipt,
        HistoricalAdmissibilityEvidenceAdmissionReceipt,
    )
    assert receipt.receipt_id == "HAEAR-000001"
    assert receipt.assessment_id == "HAEAA-000001"
    assert receipt.trust_receipt_id == "HAETR-000001"
    assert receipt.trust_receipt_hash == "a" * 64
    assert receipt.admission_status == "HOLD"
    assert receipt.policy_version == "historical-evidence-admission-v1"
    assert receipt.recorded_at == "2026-07-16T21:30:00Z"


@pytest.mark.parametrize(
    "admission_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_preserves_admission_status(
    admission_status: str,
) -> None:
    receipt = create_receipt(
        admission_status=admission_status,
    )

    assert receipt.admission_status == admission_status


def test_service_rejects_none_assessment() -> None:
    service = HistoricalAdmissibilityEvidenceAdmissionReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAEAR-000001",
            assessment=None,
            assessment_hash="a" * 64,
            recorded_at="2026-07-16T21:30:00Z",
        )


def test_service_rejects_non_matching_assessment_hash() -> None:
    service = HistoricalAdmissibilityEvidenceAdmissionReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAEAR-000001",
            assessment=make_assessment(),
            assessment_hash="b" * 64,
            recorded_at="2026-07-16T21:30:00Z",
        )


@pytest.mark.parametrize(
    "assessment_hash",
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
def test_service_rejects_invalid_assessment_hash(
    assessment_hash: str | None,
) -> None:
    service = HistoricalAdmissibilityEvidenceAdmissionReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAEAR-000001",
            assessment=make_assessment(),
            assessment_hash=assessment_hash,
            recorded_at="2026-07-16T21:30:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    receipt = create_receipt(
        admission_status="PASS",
    )

    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_service_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment
    assessment_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(assessment)
    )

    HistoricalAdmissibilityEvidenceAdmissionReceiptService().create_receipt(
        receipt_id="HAEAR-000001",
        assessment=assessment,
        assessment_hash=assessment_hash,
        recorded_at="2026-07-16T21:30:00Z",
    )

    assert assessment == original
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_pass_receipt_does_not_admit_evidence() -> None:
    receipt = create_receipt(
        admission_status="PASS",
    )

    assert receipt.admission_status == "PASS"
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False