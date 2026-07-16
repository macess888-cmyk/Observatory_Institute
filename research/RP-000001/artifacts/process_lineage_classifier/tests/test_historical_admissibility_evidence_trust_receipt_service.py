import pytest

from models.historical_admissibility_evidence_trust_assessment import (
    HistoricalAdmissibilityEvidenceTrustAssessment,
)
from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)
from services.historical_admissibility_evidence_trust_assessment_hasher import (
    HistoricalAdmissibilityEvidenceTrustAssessmentHasher,
)
from services.historical_admissibility_evidence_trust_receipt_service import (
    HistoricalAdmissibilityEvidenceTrustReceiptService,
)


def make_assessment(
    *,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
) -> HistoricalAdmissibilityEvidenceTrustAssessment:
    return HistoricalAdmissibilityEvidenceTrustAssessment(
        assessment_id="HAETA-000001",
        manifest_id="HAEPM-000001",
        manifest_hash="a" * 64,
        trust_status=trust_status,
        confidence_level=confidence_level,
        rationale=(
            "Source integrity is verified, but institutional trust "
            "remains unproven."
        ),
        policy_version="historical-evidence-trust-v1",
        assessed_at="2026-07-16T20:00:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def create_receipt(
    *,
    trust_status: str = "HOLD",
    confidence_level: str = "MEDIUM",
) -> HistoricalAdmissibilityEvidenceTrustReceipt:
    assessment = make_assessment(
        trust_status=trust_status,
        confidence_level=confidence_level,
    )
    assessment_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
    )

    return HistoricalAdmissibilityEvidenceTrustReceiptService().create_receipt(
        receipt_id="HAETR-000001",
        assessment=assessment,
        assessment_hash=assessment_hash,
        recorded_at="2026-07-16T20:30:00Z",
    )


def test_service_creates_receipt_from_validated_assessment() -> None:
    receipt = create_receipt()

    assert isinstance(
        receipt,
        HistoricalAdmissibilityEvidenceTrustReceipt,
    )
    assert receipt.receipt_id == "HAETR-000001"
    assert receipt.assessment_id == "HAETA-000001"
    assert receipt.manifest_id == "HAEPM-000001"
    assert receipt.manifest_hash == "a" * 64
    assert receipt.trust_status == "HOLD"
    assert receipt.confidence_level == "MEDIUM"
    assert receipt.policy_version == "historical-evidence-trust-v1"
    assert receipt.recorded_at == "2026-07-16T20:30:00Z"


@pytest.mark.parametrize(
    "trust_status",
    ["PASS", "HOLD", "REJECT"],
)
def test_service_preserves_trust_status(
    trust_status: str,
) -> None:
    receipt = create_receipt(
        trust_status=trust_status,
    )

    assert receipt.trust_status == trust_status


@pytest.mark.parametrize(
    "confidence_level",
    ["LOW", "MEDIUM", "HIGH"],
)
def test_service_preserves_confidence_level(
    confidence_level: str,
) -> None:
    receipt = create_receipt(
        confidence_level=confidence_level,
    )

    assert receipt.confidence_level == confidence_level


def test_service_rejects_none_assessment() -> None:
    service = HistoricalAdmissibilityEvidenceTrustReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAETR-000001",
            assessment=None,
            assessment_hash="a" * 64,
            recorded_at="2026-07-16T20:30:00Z",
        )


def test_service_rejects_non_matching_assessment_hash() -> None:
    service = HistoricalAdmissibilityEvidenceTrustReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAETR-000001",
            assessment=make_assessment(),
            assessment_hash="b" * 64,
            recorded_at="2026-07-16T20:30:00Z",
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
    service = HistoricalAdmissibilityEvidenceTrustReceiptService()

    with pytest.raises(ValueError):
        service.create_receipt(
            receipt_id="HAETR-000001",
            assessment=make_assessment(),
            assessment_hash=assessment_hash,
            recorded_at="2026-07-16T20:30:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    receipt = create_receipt(
        trust_status="PASS",
        confidence_level="HIGH",
    )

    assert receipt.trust_established is False
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False
    assert receipt.execution_requested is False
    assert receipt.side_effects_permitted is False


def test_service_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment
    assessment_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(assessment)
    )

    HistoricalAdmissibilityEvidenceTrustReceiptService().create_receipt(
        receipt_id="HAETR-000001",
        assessment=assessment,
        assessment_hash=assessment_hash,
        recorded_at="2026-07-16T20:30:00Z",
    )

    assert assessment == original
    assert assessment.trust_established is False
    assert assessment.evidence_admitted is False
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_pass_receipt_does_not_establish_trust() -> None:
    receipt = create_receipt(
        trust_status="PASS",
        confidence_level="HIGH",
    )

    assert receipt.trust_status == "PASS"
    assert receipt.trust_established is False
    assert receipt.evidence_admitted is False
    assert receipt.authorization_granted is False