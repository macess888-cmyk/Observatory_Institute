import hashlib
import json
from datetime import datetime, timezone

import pytest

from services.historical_signature_compromise_assessment import (
    HistoricalSignatureCompromiseAssessment,
)
from services.historical_signature_compromise_assessment_hasher import (
    HistoricalSignatureCompromiseAssessmentHashError,
    HistoricalSignatureCompromiseAssessmentHasher,
)


SIGNED_AT = datetime(2026, 7, 15, 13, 0, tzinfo=timezone.utc)
EFFECTIVE_AT = datetime(2026, 7, 15, 13, 30, tzinfo=timezone.utc)
DETECTED_AT = datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc)
RECORDED_AT = datetime(2026, 7, 15, 16, 5, tzinfo=timezone.utc)
ASSESSED_AT = datetime(2026, 7, 15, 17, 0, tzinfo=timezone.utc)

PUBLIC_KEY_FINGERPRINT = "sha256:" + ("1" * 64)


def make_assessment(
    *,
    assessment_id: str = "HSCA-001",
    receipt_id: str = "HSVR-001",
    verification_id: str = "HSV-001",
    signature_id: str = "SIG-001",
    key_id: str = "KEY-001",
    material_id: str = "PKM-001",
    compromise_event_id: str = "KCE-001",
    compromise_type: str = "PRIVATE_KEY_EXPOSURE",
    assessed_by: str = "OBSERVATORY-INSTITUTE",
    status: str = "PRE_COMPROMISE_VALID",
) -> HistoricalSignatureCompromiseAssessment:
    return HistoricalSignatureCompromiseAssessment(
        assessment_id=assessment_id,
        receipt_id=receipt_id,
        verification_id=verification_id,
        signature_id=signature_id,
        key_id=key_id,
        material_id=material_id,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        compromise_event_id=compromise_event_id,
        compromise_type=compromise_type,
        signed_at=SIGNED_AT,
        compromise_effective_at=EFFECTIVE_AT,
        compromise_detected_at=DETECTED_AT,
        compromise_recorded_at=RECORDED_AT,
        assessed_at=ASSESSED_AT,
        assessed_by=assessed_by,
        signature_precedes_compromise=True,
        signature_at_or_after_compromise=False,
        historical_validity_preserved=True,
        automatic_retroactive_invalidation=False,
        status=status,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    assessment = make_assessment()
    hasher = HistoricalSignatureCompromiseAssessmentHasher()

    canonical = hasher.canonicalize(assessment)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(assessment) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = (
        HistoricalSignatureCompromiseAssessmentHasher()
        .canonicalize(make_assessment())
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = HistoricalSignatureCompromiseAssessmentHasher()
    assessment = make_assessment()

    assert hasher.hash(assessment) == hasher.hash(
        assessment
    )


def test_equivalent_assessments_produce_same_hash() -> None:
    hasher = HistoricalSignatureCompromiseAssessmentHasher()

    assert hasher.hash(make_assessment()) == hasher.hash(
        make_assessment()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("assessment_id", "HSCA-999"),
        ("receipt_id", "HSVR-999"),
        ("verification_id", "HSV-999"),
        ("signature_id", "SIG-999"),
        ("key_id", "KEY-999"),
        ("material_id", "PKM-999"),
        ("compromise_event_id", "KCE-999"),
        ("compromise_type", "UNAUTHORIZED_KEY_USE"),
        ("assessed_by", "OTHER-ASSESSOR"),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = HistoricalSignatureCompromiseAssessmentHasher()

    baseline = hasher.hash(make_assessment())
    changed = hasher.hash(
        make_assessment(**{field_name: value})
    )

    assert baseline != changed


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        (
            "signed_at",
            datetime(2026, 7, 15, 12, 59, tzinfo=timezone.utc),
        ),
        (
            "compromise_effective_at",
            datetime(2026, 7, 15, 13, 31, tzinfo=timezone.utc),
        ),
        (
            "compromise_detected_at",
            datetime(2026, 7, 15, 16, 1, tzinfo=timezone.utc),
        ),
        (
            "compromise_recorded_at",
            datetime(2026, 7, 15, 16, 6, tzinfo=timezone.utc),
        ),
        (
            "assessed_at",
            datetime(2026, 7, 15, 17, 1, tzinfo=timezone.utc),
        ),
    ],
)
def test_changed_time_changes_hash(
    field_name: str,
    value: datetime,
) -> None:
    hasher = HistoricalSignatureCompromiseAssessmentHasher()
    baseline = make_assessment()
    changed = make_assessment()
    object.__setattr__(changed, field_name, value)

    assert hasher.hash(baseline) != hasher.hash(changed)


def test_changed_timing_classification_changes_hash() -> None:
    hasher = HistoricalSignatureCompromiseAssessmentHasher()
    baseline = make_assessment()
    changed = make_assessment()

    object.__setattr__(
        changed,
        "signature_precedes_compromise",
        False,
    )
    object.__setattr__(
        changed,
        "signature_at_or_after_compromise",
        True,
    )
    object.__setattr__(
        changed,
        "historical_validity_preserved",
        False,
    )
    object.__setattr__(
        changed,
        "status",
        "AT_OR_AFTER_COMPROMISE",
    )

    assert hasher.hash(baseline) != hasher.hash(changed)


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        HistoricalSignatureCompromiseAssessmentHasher()
        .canonicalize(make_assessment())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = (
        HistoricalSignatureCompromiseAssessmentHasher()
        .canonicalize(make_assessment())
    )

    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )

    assert tuple(decoded.keys()) == (
        "assessment_id",
        "receipt_id",
        "verification_id",
        "signature_id",
        "key_id",
        "material_id",
        "public_key_fingerprint",
        "compromise_event_id",
        "compromise_type",
        "signed_at",
        "compromise_effective_at",
        "compromise_detected_at",
        "compromise_recorded_at",
        "assessed_at",
        "assessed_by",
        "signature_precedes_compromise",
        "signature_at_or_after_compromise",
        "historical_validity_preserved",
        "automatic_retroactive_invalidation",
        "status",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamps() -> None:
    canonical_text = (
        HistoricalSignatureCompromiseAssessmentHasher()
        .canonicalize(make_assessment())
        .decode("utf-8")
    )

    assert SIGNED_AT.isoformat() in canonical_text
    assert EFFECTIVE_AT.isoformat() in canonical_text
    assert DETECTED_AT.isoformat() in canonical_text
    assert RECORDED_AT.isoformat() in canonical_text
    assert ASSESSED_AT.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = (
        HistoricalSignatureCompromiseAssessmentHasher()
        .canonicalize(make_assessment())
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["assessment_id"] == "HSCA-001"
    assert decoded["signature_precedes_compromise"] is True
    assert decoded["signature_at_or_after_compromise"] is False
    assert decoded["historical_validity_preserved"] is True
    assert (
        decoded["automatic_retroactive_invalidation"]
        is False
    )
    assert decoded["status"] == "PRE_COMPROMISE_VALID"
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_assessment_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureCompromiseAssessment",
    ):
        HistoricalSignatureCompromiseAssessmentHasher().hash(
            "HSCA-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_assessment_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureCompromiseAssessment",
    ):
        HistoricalSignatureCompromiseAssessmentHasher().canonicalize(
            "HSCA-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = HistoricalSignatureCompromiseAssessmentHasher()
    assessment = make_assessment()
    digest = hasher.hash(assessment)

    assert hasher.validate(assessment, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentHashError,
        match="hash mismatch",
    ):
        HistoricalSignatureCompromiseAssessmentHasher().validate(
            make_assessment(),
            "sha256:" + ("9" * 64),
        )


@pytest.mark.parametrize(
    "digest",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
        "sha256:" + ("A" * 64),
    ],
)
def test_validate_rejects_invalid_expected_digest(
    digest: str,
) -> None:
    with pytest.raises(
        HistoricalSignatureCompromiseAssessmentHashError,
        match="expected_digest",
    ):
        HistoricalSignatureCompromiseAssessmentHasher().validate(
            make_assessment(),
            digest,
        )


def test_hasher_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment

    HistoricalSignatureCompromiseAssessmentHasher().hash(
        assessment
    )

    assert assessment == original


def test_hash_preserves_non_retroactive_boundary() -> None:
    canonical = (
        HistoricalSignatureCompromiseAssessmentHasher()
        .canonicalize(make_assessment())
    )
    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["historical_validity_preserved"] is True
    assert (
        decoded["automatic_retroactive_invalidation"]
        is False
    )


def test_assessment_preserves_observer_only_boundary() -> None:
    assessment = make_assessment()

    assert assessment.execution_requested is False
    assert assessment.side_effects_permitted is False