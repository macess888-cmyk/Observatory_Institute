from datetime import datetime, timezone

import pytest

from models import (
    HistoricalSignatureVerificationReceipt,
    KeyCompromiseEvent,
)
from services.historical_signature_compromise_assessment import (
    HistoricalSignatureCompromiseAssessment,
    HistoricalSignatureCompromiseAssessmentError,
    HistoricalSignatureCompromiseAssessmentService,
)


SIGNED_BEFORE = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
SIGNED_AFTER = datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)
VERIFIED_AT = datetime(2026, 7, 15, 17, 0, tzinfo=timezone.utc)

EFFECTIVE_AT = datetime(2026, 7, 15, 13, 30, tzinfo=timezone.utc)
DETECTED_AT = datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc)
RECORDED_AT = datetime(2026, 7, 15, 16, 5, tzinfo=timezone.utc)

CONTENT_DIGEST = "sha256:" + ("1" * 64)
PAYLOAD_DIGEST = "sha256:" + ("2" * 64)
PUBLIC_KEY_FINGERPRINT = "sha256:" + ("3" * 64)
SIGNING_SNAPSHOT_DIGEST = "sha256:" + ("4" * 64)
VERIFICATION_SNAPSHOT_DIGEST = "sha256:" + ("5" * 64)
EVIDENCE_DIGEST = "sha256:" + ("6" * 64)


def make_receipt(
    *,
    signed_at: datetime = SIGNED_BEFORE,
    key_id: str = "KEY-001",
    material_id: str = "PKM-001",
) -> HistoricalSignatureVerificationReceipt:
    return HistoricalSignatureVerificationReceipt(
        receipt_id="HSVR-001",
        verification_id="HSV-001",
        signature_id="SIG-001",
        key_id=key_id,
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
        signed_at=signed_at,
        verified_at=VERIFIED_AT,
        mathematical_verification=True,
        identity_match=True,
        content_match=True,
        signing_time_key_present=True,
        verification_time_key_present=False,
        key_valid_at_signing=True,
        verified=True,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_event(
    *,
    key_id: str = "KEY-001",
    material_id: str = "PKM-001",
    effective_at: datetime = EFFECTIVE_AT,
) -> KeyCompromiseEvent:
    return KeyCompromiseEvent(
        event_id="KCE-001",
        key_id=key_id,
        material_id=material_id,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        compromise_type="PRIVATE_KEY_EXPOSURE",
        evidence_digest=EVIDENCE_DIGEST,
        detected_at=DETECTED_AT,
        effective_at=effective_at,
        recorded_at=RECORDED_AT,
        reported_by="OBSERVATORY-INSTITUTE",
        description="Private-key exposure was independently observed.",
        confirmed=True,
        historical_signatures_invalidated=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def assess(
    receipt: HistoricalSignatureVerificationReceipt,
    event: KeyCompromiseEvent,
) -> HistoricalSignatureCompromiseAssessment:
    return HistoricalSignatureCompromiseAssessmentService().assess(
        assessment_id="HSCA-001",
        receipt=receipt,
        compromise_event=event,
        assessed_by="OBSERVATORY-INSTITUTE",
        assessed_at=VERIFIED_AT,
    )


def test_signature_before_effective_compromise_is_pre_compromise() -> None:
    assessment = assess(
        make_receipt(signed_at=SIGNED_BEFORE),
        make_event(),
    )

    assert assessment.signature_precedes_compromise is True
    assert assessment.signature_at_or_after_compromise is False
    assert assessment.historical_validity_preserved is True
    assert assessment.status == "PRE_COMPROMISE_VALID"
    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False


def test_signature_after_effective_compromise_is_exposed() -> None:
    assessment = assess(
        make_receipt(signed_at=SIGNED_AFTER),
        make_event(),
    )

    assert assessment.signature_precedes_compromise is False
    assert assessment.signature_at_or_after_compromise is True
    assert assessment.historical_validity_preserved is False
    assert assessment.status == "AT_OR_AFTER_COMPROMISE"


def test_signature_exactly_at_effective_time_is_exposed() -> None:
    assessment = assess(
        make_receipt(signed_at=EFFECTIVE_AT),
        make_event(),
    )

    assert assessment.signature_at_or_after_compromise is True
    assert assessment.status == "AT_OR_AFTER_COMPROMISE"


def test_detection_time_does_not_define_signature_validity_boundary() -> None:
    receipt = make_receipt(
        signed_at=datetime(
            2026,
            7,
            15,
            15,
            0,
            tzinfo=timezone.utc,
        )
    )
    assessment = assess(receipt, make_event())

    assert receipt.signed_at < DETECTED_AT
    assert receipt.signed_at >= EFFECTIVE_AT
    assert assessment.status == "AT_OR_AFTER_COMPROMISE"


def test_service_rejects_key_identity_mismatch() -> None:
    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match="key identity",
    ):
        assess(
            make_receipt(key_id="KEY-001"),
            make_event(key_id="KEY-999"),
        )


def test_service_rejects_fingerprint_mismatch() -> None:
    event = make_event()
    object.__setattr__(
        event,
        "public_key_fingerprint",
        "sha256:" + ("9" * 64),
    )

    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match="fingerprint",
    ):
        assess(make_receipt(), event)


def test_service_rejects_unverified_receipt() -> None:
    receipt = make_receipt()
    object.__setattr__(receipt, "verified", False)

    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match="verified receipt",
    ):
        assess(receipt, make_event())


def test_service_rejects_unconfirmed_compromise_event() -> None:
    event = make_event()
    object.__setattr__(event, "confirmed", False)

    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match="confirmed compromise",
    ):
        assess(make_receipt(), event)


def test_service_rejects_non_receipt_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureVerificationReceipt",
    ):
        HistoricalSignatureCompromiseAssessmentService().assess(
            assessment_id="HSCA-001",
            receipt="HSVR-001",  # type: ignore[arg-type]
            compromise_event=make_event(),
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=VERIFIED_AT,
        )


def test_service_rejects_non_event_input() -> None:
    with pytest.raises(
        TypeError,
        match="KeyCompromiseEvent",
    ):
        HistoricalSignatureCompromiseAssessmentService().assess(
            assessment_id="HSCA-001",
            receipt=make_receipt(),
            compromise_event="KCE-001",  # type: ignore[arg-type]
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=VERIFIED_AT,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "assessment_id",
        "assessed_by",
    ],
)
def test_service_rejects_empty_identity(
    field_name: str,
) -> None:
    arguments = {
        "assessment_id": "HSCA-001",
        "receipt": make_receipt(),
        "compromise_event": make_event(),
        "assessed_by": "OBSERVATORY-INSTITUTE",
        "assessed_at": VERIFIED_AT,
    }
    arguments[field_name] = ""

    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match=field_name,
    ):
        HistoricalSignatureCompromiseAssessmentService().assess(
            **arguments
        )


def test_service_rejects_naive_assessed_at() -> None:
    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match="assessed_at.*timezone-aware",
    ):
        HistoricalSignatureCompromiseAssessmentService().assess(
            assessment_id="HSCA-001",
            receipt=make_receipt(),
            compromise_event=make_event(),
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=datetime(2026, 7, 15, 17, 0),
        )


def test_service_rejects_assessment_before_compromise_recording() -> None:
    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentError,
        match="before compromise recording",
    ):
        HistoricalSignatureCompromiseAssessmentService().assess(
            assessment_id="HSCA-001",
            receipt=make_receipt(),
            compromise_event=make_event(),
            assessed_by="OBSERVATORY-INSTITUTE",
            assessed_at=datetime(
                2026,
                7,
                15,
                16,
                4,
                tzinfo=timezone.utc,
            ),
        )


def test_service_is_deterministic() -> None:
    receipt = make_receipt()
    event = make_event()

    assert assess(receipt, event) == assess(receipt, event)


def test_service_does_not_mutate_inputs() -> None:
    receipt = make_receipt()
    event = make_event()
    original_receipt = receipt
    original_event = event

    assess(receipt, event)

    assert receipt == original_receipt
    assert event == original_event


def test_assessment_preserves_non_retroactive_boundary() -> None:
    assessment = assess(make_receipt(), make_event())

    assert assessment.historical_validity_preserved is True
    assert assessment.automatic_retroactive_invalidation is False


def test_assessment_preserves_observer_only_boundary() -> None:
    assessment = assess(make_receipt(), make_event())

    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False