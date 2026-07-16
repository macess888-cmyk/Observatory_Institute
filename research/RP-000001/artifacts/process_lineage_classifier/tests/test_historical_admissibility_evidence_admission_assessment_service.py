import pytest

from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)
from models.historical_admissibility_evidence_admission_assessment import (
    HistoricalAdmissibilityEvidenceAdmissionAssessment,
)
from services.historical_admissibility_evidence_trust_receipt_hasher import (
    HistoricalAdmissibilityEvidenceTrustReceiptHasher,
)
from services.historical_admissibility_evidence_admission_assessment_service import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentService,
)


def make_trust_receipt(
    *,
    trust_status: str = "PASS",
    confidence_level: str = "HIGH",
) -> HistoricalAdmissibilityEvidenceTrustReceipt:
    return HistoricalAdmissibilityEvidenceTrustReceipt(
        receipt_id="HAETR-000001",
        assessment_id="HAETA-000001",
        assessment_hash="a" * 64,
        manifest_id="HAEPM-000001",
        manifest_hash="b" * 64,
        trust_status=trust_status,
        confidence_level=confidence_level,
        policy_version="historical-evidence-trust-v1",
        recorded_at="2026-07-16T20:30:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def create_assessment(
    *,
    admission_status: str = "HOLD",
) -> HistoricalAdmissibilityEvidenceAdmissionAssessment:
    trust_receipt = make_trust_receipt()
    trust_receipt_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(trust_receipt)
    )

    return HistoricalAdmissibilityEvidenceAdmissionAssessmentService().assess(
        assessment_id="HAEAA-000001",
        trust_receipt=trust_receipt,
        trust_receipt_hash=trust_receipt_hash,
        admission_status=admission_status,
        rationale=(
            "Trust evidence is recorded, but governance admission "
            "criteria remain incomplete."
        ),
        policy_version="historical-evidence-admission-v1",
        assessed_at="2026-07-16T21:00:00Z",
    )


def test_service_creates_assessment_from_validated_trust_receipt() -> None:
    assessment = create_assessment()

    assert isinstance(
        assessment,
        HistoricalAdmissibilityEvidenceAdmissionAssessment,
    )
    assert assessment.assessment_id == "HAEAA-000001"
    assert assessment.trust_receipt_id == "HAETR-000001"
    assert assessment.admission_status == "HOLD"
    assert assessment.policy_version == "historical-evidence-admission-v1"
    assert assessment.assessed_at == "2026-07-16T21:00:00Z"


@pytest.mark.parametrize(
    "admission_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_supports_all_admission_statuses(
    admission_status: str,
) -> None:
    assessment = create_assessment(
        admission_status=admission_status,
    )

    assert assessment.admission_status == admission_status


def test_service_rejects_none_trust_receipt() -> None:
    service = HistoricalAdmissibilityEvidenceAdmissionAssessmentService()

    with pytest.raises(ValueError):
        service.assess(
            assessment_id="HAEAA-000001",
            trust_receipt=None,
            trust_receipt_hash="a" * 64,
            admission_status="HOLD",
            rationale="Trust receipt is missing.",
            policy_version="historical-evidence-admission-v1",
            assessed_at="2026-07-16T21:00:00Z",
        )


def test_service_rejects_non_matching_trust_receipt_hash() -> None:
    service = HistoricalAdmissibilityEvidenceAdmissionAssessmentService()

    with pytest.raises(ValueError):
        service.assess(
            assessment_id="HAEAA-000001",
            trust_receipt=make_trust_receipt(),
            trust_receipt_hash="c" * 64,
            admission_status="HOLD",
            rationale="Trust receipt integrity could not be confirmed.",
            policy_version="historical-evidence-admission-v1",
            assessed_at="2026-07-16T21:00:00Z",
        )


@pytest.mark.parametrize(
    "trust_receipt_hash",
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
def test_service_rejects_invalid_trust_receipt_hash(
    trust_receipt_hash: str | None,
) -> None:
    service = HistoricalAdmissibilityEvidenceAdmissionAssessmentService()

    with pytest.raises(ValueError):
        service.assess(
            assessment_id="HAEAA-000001",
            trust_receipt=make_trust_receipt(),
            trust_receipt_hash=trust_receipt_hash,
            admission_status="HOLD",
            rationale="Trust receipt hash is invalid.",
            policy_version="historical-evidence-admission-v1",
            assessed_at="2026-07-16T21:00:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    assessment = create_assessment(
        admission_status="PASS",
    )

    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_service_does_not_mutate_trust_receipt() -> None:
    trust_receipt = make_trust_receipt()
    original = trust_receipt
    trust_receipt_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(trust_receipt)
    )

    HistoricalAdmissibilityEvidenceAdmissionAssessmentService().assess(
        assessment_id="HAEAA-000001",
        trust_receipt=trust_receipt,
        trust_receipt_hash=trust_receipt_hash,
        admission_status="HOLD",
        rationale="Admission remains under assessment.",
        policy_version="historical-evidence-admission-v1",
        assessed_at="2026-07-16T21:00:00Z",
    )

    assert trust_receipt == original
    assert trust_receipt.trust_established is False
    assert trust_receipt.evidence_admitted is False
    assert trust_receipt.authorization_granted is False
    assert trust_receipt.execution_requested is False
    assert trust_receipt.side_effects_permitted is False


def test_pass_assessment_does_not_admit_evidence() -> None:
    assessment = create_assessment(
        admission_status="PASS",
    )

    assert assessment.admission_status == "PASS"
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False