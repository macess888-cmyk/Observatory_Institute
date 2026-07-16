from datetime import datetime, timezone

import pytest

from models import HistoricalSignatureVerificationReceipt
from services.historical_signature_admissibility import (
    HistoricalSignatureAdmissibilityAssessment,
    HistoricalSignatureAdmissibilityError,
    HistoricalSignatureAdmissibilityService,
)
from services.historical_signature_compromise_assessment import (
    HistoricalSignatureCompromiseAssessment,
)


ASSESSED_AT = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)
SIGNED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 17, 0, tzinfo=timezone.utc)
EFFECTIVE_AT = datetime(2026, 7, 15, 13, 30, tzinfo=timezone.utc)
DETECTED_AT = datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc)
RECORDED_AT = datetime(2026, 7, 15, 16, 5, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
PAYLOAD_DIGEST = "sha256:" + ("2" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("3" * 64)
SIGNING_SNAPSHOT_DIGEST = "sha256:" + ("4" * 64)
VERIFICATION_SNAPSHOT_DIGEST = "sha256:" + ("5" * 64)


def make_receipt(
    *,
    verified: bool = True,
) -> HistoricalSignatureVerificationReceipt:
    return HistoricalSignatureVerificationReceipt(
        receipt_id="HSVR-001",
        verification_id="HSV-001",
        signature_id="SIG-001",
        key_id="KEY-001",
        subject_id="RIB-001",
        subject_type="RECOVERY_INTEGRITY_BUNDLE",
        content_digest=CONTENT_DIGEST,
        payload_digest=PAYLOAD_DIGEST,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        algorithm="ED25519",
        signer_id="PROCESS-LINEAGE-CLASSIFIER",
        verifier_id="OBSERVATORY-INSTITUTE",
        registry_id="TKR-001",
        signing_registry_version="1.0.0",
        signing_snapshot_id="TKRS-100",
        signing_snapshot_digest=SIGNING_SNAPSHOT_DIGEST,
        verification_registry_version="1.2.0",
        verification_snapshot_id="TKRS-120",
        verification_snapshot_digest=VERIFICATION_SNAPSHOT_DIGEST,
        signed_at=SIGNED_AT,
        verified_at=VERIFIED_AT,
        mathematical_verification=verified,
        identity_match=verified,
        content_match=verified,
        signing_time_key_present=verified,
        verification_time_key_present=False,
        key_valid_at_signing=verified,
        verified=verified,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_compromise_assessment(
    *,
    historical_validity_preserved: bool = True,
    status: str = "PRE_COMPROMISE_VALID",
) -> HistoricalSignatureCompromiseAssessment:
    precedes = historical_validity_preserved

    return HistoricalSignatureCompromiseAssessment(
        assessment_id="HSCA-001",
        receipt_id="HSVR-001",
        verification_id="HSV-001",
        signature_id="SIG-001",
        key_id="KEY-001",
        material_id="PKM-001",
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        compromise_event_id="KCE-001",
        compromise_type="PRIVATE_KEY_EXPOSURE",
        signed_at=SIGNED_AT,
        compromise_effective_at=EFFECTIVE_AT,
        compromise_detected_at=DETECTED_AT,
        compromise_recorded_at=RECORDED_AT,
        assessed_at=ASSESSED_AT,
        assessed_by="OBSERVATORY-INSTITUTE",
        signature_precedes_compromise=precedes,
        signature_at_or_after_compromise=not precedes,
        historical_validity_preserved=historical_validity_preserved,
        automatic_retroactive_invalidation=False,
        status=status,
        execution_requested=False,
        side_effects_permitted=False,
    )


def assess(
    *,
    receipt: HistoricalSignatureVerificationReceipt | None,
    compromise_assessment: (
        HistoricalSignatureCompromiseAssessment | None
    ),
) -> HistoricalSignatureAdmissibilityAssessment:
    return HistoricalSignatureAdmissibilityService().assess(
        admissibility_id="HSAA-001",
        receipt=receipt,
        compromise_assessment=compromise_assessment,
        assessed_by="OBSERVATORY-INSTITUTE",
        assessed_at=ASSESSED_AT,
    )


def test_service_returns_pass_for_verified_pre_compromise_signature() -> None:
    assessment = assess(
        receipt=make_receipt(),
        compromise_assessment=make_compromise_assessment(),
    )

    assert assessment.outcome == "PASS"
    assert assessment.admissible is True
    assert assessment.hold_required is False
    assert assessment.rejected is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_service_returns_reject_for_at_or_after_compromise_signature() -> None:
    assessment = assess(
        receipt=make_receipt(),
        compromise_assessment=make_compromise_assessment(
            historical_validity_preserved=False,
            status="AT_OR_AFTER_COMPROMISE",
        ),
    )

    assert assessment.outcome == "REJECT"
    assert assessment.admissible is False
    assert assessment.hold_required is False
    assert assessment.rejected is True


def test_service_returns_hold_when_compromise_assessment_missing() -> None:
    assessment = assess(
        receipt=make_receipt(),
        compromise_assessment=None,
    )

    assert assessment.outcome == "HOLD"
    assert assessment.admissible is False
    assert assessment.hold_required is True
    assert assessment.rejected is False


def test_service_returns_hold_when_verification_receipt_missing() -> None:
    assessment = assess(
        receipt=None,
        compromise_assessment=make_compromise_assessment(),
    )

    assert assessment.outcome == "HOLD"
    assert assessment.admissible is False
    assert assessment.hold_required is True
    assert assessment.rejected is False


def test_service_rejects_unverified_receipt() -> None:
    receipt = make_receipt()
    object.__setattr__(receipt, "verified", False)

    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="verified receipt",
    ):
        assess(
            receipt=receipt,
            compromise_assessment=make_compromise_assessment(),
        )


def test_service_rejects_receipt_assessment_identity_mismatch() -> None:
    compromise = make_compromise_assessment()
    object.__setattr__(
        compromise,
        "receipt_id",
        "HSVR-999",
    )

    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="receipt identity",
    ):
        assess(
            receipt=make_receipt(),
            compromise_assessment=compromise,
        )


def test_service_rejects_signature_identity_mismatch() -> None:
    compromise = make_compromise_assessment()
    object.__setattr__(
        compromise,
        "signature_id",
        "SIG-999",
    )

    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="signature identity",
    ):
        assess(
            receipt=make_receipt(),
            compromise_assessment=compromise,
        )


def test_service_rejects_key_identity_mismatch() -> None:
    compromise = make_compromise_assessment()
    object.__setattr__(
        compromise,
        "key_id",
        "KEY-999",
    )

    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="key identity",
    ):
        assess(
            receipt=make_receipt(),
            compromise_assessment=compromise,
        )


def test_service_rejects_fingerprint_mismatch() -> None:
    compromise = make_compromise_assessment()
    object.__setattr__(
        compromise,
        "public_key_fingerprint",
        "sha256:" + ("9" * 64),
    )

    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="fingerprint",
    ):
        assess(
            receipt=make_receipt(),
            compromise_assessment=compromise,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "admissibility_id",
        "assessed_by",
    ],
)
def test_service_rejects_empty_identity(
    field_name: str,
) -> None:
    arguments = {
        "admissibility_id": "HSAA-001",
        "receipt": make_receipt(),
        "compromise_assessment": make_compromise_assessment(),
        "assessed_by": "OBSERVATORY-INSTITUTE",
        "assessed_at": ASSESSED_AT,
    }
    arguments[field_name] = ""

    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match=field_name,
    ):
        HistoricalSignatureAdmissibilityService().assess(
            **arguments
        )


def test_service_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureVerificationReceipt",
    ):
        HistoricalSignatureAdmissibilityService().assess(
            admissibility_id="HSAA-001",
            receipt="HSVR-001",  # type: ignore[arg-type]
            compromise_assessment=make_compromise_assessment(),
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=ASSESSED_AT,
        )


def test_service_rejects_non_assessment_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureCompromiseAssessment",
    ):
        HistoricalSignatureAdmissibilityService().assess(
            admissibility_id="HSAA-001",
            receipt=make_receipt(),
            compromise_assessment="HSCA-001",  # type: ignore[arg-type]
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=ASSESSED_AT,
        )


def test_service_rejects_naive_assessed_at() -> None:
    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="assessed_at.*timezone-aware",
    ):
        HistoricalSignatureAdmissibilityService().assess(
            admissibility_id="HSAA-001",
            receipt=make_receipt(),
            compromise_assessment=make_compromise_assessment(),
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=datetime(2026, 7, 15, 18, 0),
        )


def test_service_rejects_assessment_before_verification() -> None:
    with pytest.raises(
        HistoricalSignatureAdmissibilityError,
        match="before verification",
    ):
        HistoricalSignatureAdmissibilityService().assess(
            admissibility_id="HSAA-001",
            receipt=make_receipt(),
            compromise_assessment=make_compromise_assessment(),
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=datetime(
                2026,
                7,
                15,
                16,
                59,
                tzinfo=timezone.utc,
            ),
        )


def test_service_is_deterministic() -> None:
    receipt = make_receipt()
    compromise = make_compromise_assessment()

    first = assess(
        receipt=receipt,
        compromise_assessment=compromise,
    )
    second = assess(
        receipt=receipt,
        compromise_assessment=compromise,
    )

    assert first == second


def test_service_does_not_mutate_inputs() -> None:
    receipt = make_receipt()
    compromise = make_compromise_assessment()
    original_receipt = receipt
    original_compromise = compromise

    assess(
        receipt=receipt,
        compromise_assessment=compromise,
    )

    assert receipt == original_receipt
    assert compromise == original_compromise


def test_pass_does_not_grant_authority_or_execution() -> None:
    assessment = assess(
        receipt=make_receipt(),
        compromise_assessment=make_compromise_assessment(),
    )

    assert assessment.outcome == "PASS"
    assert assessment.authorization_granted is False
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_hold_preserves_unknown_to_hold_boundary() -> None:
    assessment = assess(
        receipt=make_receipt(),
        compromise_assessment=None,
    )

    assert assessment.outcome == "HOLD"
    assert assessment.hold_required is True
    assert assessment.authorization_granted is False