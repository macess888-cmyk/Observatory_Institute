import hashlib
import json
from datetime import datetime, timezone

import pytest

from services.historical_signature_admissibility import (
    HistoricalSignatureAdmissibilityAssessment,
)
from services.historical_signature_admissibility_hasher import (
    HistoricalSignatureAdmissibilityAssessmentHashError,
    HistoricalSignatureAdmissibilityAssessmentHasher,
)


ASSESSED_AT = datetime(2026, 7, 15, 18, 0, tzinfo=timezone.utc)

PUBLIC_KEY_FINGERPRINT = "sha256:" + ("1" * 64)


def make_assessment(
    *,
    admissibility_id: str = "HSAA-001",
    receipt_id: str | None = "HSVR-001",
    verification_id: str | None = "HSV-001",
    signature_id: str | None = "SIG-001",
    key_id: str | None = "KEY-001",
    public_key_fingerprint: str | None = (
        PUBLIC_KEY_FINGERPRINT
    ),
    compromise_assessment_id: str | None = "HSCA-001",
    compromise_event_id: str | None = "KCE-001",
    assessed_by: str = "OBSERVATORY-INSTITUTE",
    outcome: str = "PASS",
) -> HistoricalSignatureAdmissibilityAssessment:
    if outcome == "PASS":
        verification_evidence_available = True
        compromise_evidence_available = True
        historical_validity_preserved = True
        admissible = True
        hold_required = False
        rejected = False
    elif outcome == "HOLD":
        verification_evidence_available = receipt_id is not None
        compromise_evidence_available = (
            compromise_assessment_id is not None
        )
        historical_validity_preserved = None
        admissible = False
        hold_required = True
        rejected = False
    else:
        verification_evidence_available = True
        compromise_evidence_available = True
        historical_validity_preserved = False
        admissible = False
        hold_required = False
        rejected = True

    return HistoricalSignatureAdmissibilityAssessment(
        admissibility_id=admissibility_id,
        receipt_id=receipt_id,
        verification_id=verification_id,
        signature_id=signature_id,
        key_id=key_id,
        public_key_fingerprint=public_key_fingerprint,
        compromise_assessment_id=compromise_assessment_id,
        compromise_event_id=compromise_event_id,
        assessed_by=assessed_by,
        assessed_at=ASSESSED_AT,
        verification_evidence_available=(
            verification_evidence_available
        ),
        compromise_evidence_available=(
            compromise_evidence_available
        ),
        historical_validity_preserved=(
            historical_validity_preserved
        ),
        outcome=outcome,
        admissible=admissible,
        hold_required=hold_required,
        rejected=rejected,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    assessment = make_assessment()
    hasher = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
    )

    canonical = hasher.canonicalize(assessment)
    expected = "sha256:" + hashlib.sha256(
        canonical
    ).hexdigest()

    assert hasher.hash(assessment) == expected


def test_canonicalization_returns_bytes() -> None:
    canonical = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(make_assessment())
    )

    assert isinstance(canonical, bytes)


def test_hashing_is_deterministic() -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()
    assessment = make_assessment()

    assert hasher.hash(assessment) == hasher.hash(
        assessment
    )


def test_equivalent_assessments_produce_same_hash() -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()

    assert hasher.hash(make_assessment()) == hasher.hash(
        make_assessment()
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("admissibility_id", "HSAA-999"),
        ("receipt_id", "HSVR-999"),
        ("verification_id", "HSV-999"),
        ("signature_id", "SIG-999"),
        ("key_id", "KEY-999"),
        (
            "public_key_fingerprint",
            "sha256:" + ("9" * 64),
        ),
        (
            "compromise_assessment_id",
            "HSCA-999",
        ),
        ("compromise_event_id", "KCE-999"),
        ("assessed_by", "OTHER-ASSESSOR"),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()

    baseline = hasher.hash(make_assessment())
    changed = hasher.hash(
        make_assessment(**{field_name: value})
    )

    assert baseline != changed


@pytest.mark.parametrize(
    "outcome",
    [
        "PASS",
        "HOLD",
        "REJECT",
    ],
)
def test_each_outcome_produces_valid_canonical_hash(
    outcome: str,
) -> None:
    kwargs: dict[str, object] = {"outcome": outcome}

    if outcome == "HOLD":
        kwargs["compromise_assessment_id"] = None
        kwargs["compromise_event_id"] = None

    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()
    assessment = make_assessment(**kwargs)

    digest = hasher.hash(assessment)

    assert digest.startswith("sha256:")
    assert len(digest) == 71


def test_outcome_change_changes_hash() -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()

    passed = make_assessment(outcome="PASS")
    rejected = make_assessment(outcome="REJECT")

    assert hasher.hash(passed) != hasher.hash(rejected)


def test_missing_evidence_changes_hash() -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()

    passed = make_assessment(outcome="PASS")
    held = make_assessment(
        outcome="HOLD",
        compromise_assessment_id=None,
        compromise_event_id=None,
    )

    assert hasher.hash(passed) != hasher.hash(held)


def test_changed_assessed_time_changes_hash() -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()
    baseline = make_assessment()
    changed = make_assessment()

    object.__setattr__(
        changed,
        "assessed_at",
        datetime(
            2026,
            7,
            15,
            18,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert hasher.hash(baseline) != hasher.hash(changed)


def test_canonical_payload_has_no_extra_whitespace() -> None:
    canonical_text = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(make_assessment())
        .decode("utf-8")
    )

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(make_assessment())
    )

    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )

    assert tuple(decoded.keys()) == (
        "admissibility_id",
        "receipt_id",
        "verification_id",
        "signature_id",
        "key_id",
        "public_key_fingerprint",
        "compromise_assessment_id",
        "compromise_event_id",
        "assessed_by",
        "assessed_at",
        "verification_evidence_available",
        "compromise_evidence_available",
        "historical_validity_preserved",
        "outcome",
        "admissible",
        "hold_required",
        "rejected",
        "authorization_granted",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamp() -> None:
    canonical_text = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(make_assessment())
        .decode("utf-8")
    )

    assert ASSESSED_AT.isoformat() in canonical_text


def test_canonical_payload_is_valid_json() -> None:
    canonical = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(make_assessment())
    )

    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["admissibility_id"] == "HSAA-001"
    assert decoded["outcome"] == "PASS"
    assert decoded["admissible"] is True
    assert decoded["hold_required"] is False
    assert decoded["rejected"] is False
    assert decoded["authorization_granted"] is False
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_assessment_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureAdmissibilityAssessment",
    ):
        HistoricalSignatureAdmissibilityAssessmentHasher().hash(
            "HSAA-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_assessment_input() -> None:
    with pytest.raises(
        TypeError,
        match="HistoricalSignatureAdmissibilityAssessment",
    ):
        HistoricalSignatureAdmissibilityAssessmentHasher().canonicalize(
            "HSAA-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = HistoricalSignatureAdmissibilityAssessmentHasher()
    assessment = make_assessment()
    digest = hasher.hash(assessment)

    assert hasher.validate(assessment, digest) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        HistoricalSignatureAdmissibilityAssessmentHashError,
        match="hash mismatch",
    ):
        HistoricalSignatureAdmissibilityAssessmentHasher().validate(
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
        HistoricalSignatureAdmissibilityAssessmentHashError,
        match="expected_digest",
    ):
        HistoricalSignatureAdmissibilityAssessmentHasher().validate(
            make_assessment(),
            digest,
        )


def test_hasher_does_not_mutate_assessment() -> None:
    assessment = make_assessment()
    original = assessment

    HistoricalSignatureAdmissibilityAssessmentHasher().hash(
        assessment
    )

    assert assessment == original


def test_hash_preserves_unknown_to_hold_boundary() -> None:
    assessment = make_assessment(
        outcome="HOLD",
        compromise_assessment_id=None,
        compromise_event_id=None,
    )
    canonical = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(assessment)
    )
    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["outcome"] == "HOLD"
    assert decoded["hold_required"] is True
    assert decoded["authorization_granted"] is False


def test_hash_preserves_no_authorization_boundary() -> None:
    canonical = (
        HistoricalSignatureAdmissibilityAssessmentHasher()
        .canonicalize(make_assessment())
    )
    decoded = json.loads(canonical.decode("utf-8"))

    assert decoded["outcome"] == "PASS"
    assert decoded["authorization_granted"] is False
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False