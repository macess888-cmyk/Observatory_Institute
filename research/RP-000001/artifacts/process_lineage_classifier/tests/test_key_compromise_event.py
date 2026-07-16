from datetime import datetime, timezone

import pytest

from models import KeyCompromiseEvent
from services.key_compromise_event_validator import (
    KeyCompromiseEventError,
    KeyCompromiseEventValidator,
)


DETECTED_AT = datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc)
EFFECTIVE_AT = datetime(2026, 7, 15, 13, 30, tzinfo=timezone.utc)
RECORDED_AT = datetime(2026, 7, 15, 16, 5, tzinfo=timezone.utc)

PUBLIC_KEY_FINGERPRINT = "sha256:" + ("1" * 64)
EVIDENCE_DIGEST = "sha256:" + ("2" * 64)


def make_event(
    *,
    event_id: str = "KCE-001",
    key_id: str = "KEY-001",
    material_id: str = "PKM-001",
    compromise_type: str = "PRIVATE_KEY_EXPOSURE",
    detected_at: datetime = DETECTED_AT,
    effective_at: datetime = EFFECTIVE_AT,
    recorded_at: datetime = RECORDED_AT,
    historical_signatures_invalidated: bool = False,
) -> KeyCompromiseEvent:
    return KeyCompromiseEvent(
        event_id=event_id,
        key_id=key_id,
        material_id=material_id,
        public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
        owner_id="PROCESS-LINEAGE-CLASSIFIER",
        issuer_id="OBSERVATORY-INSTITUTE",
        compromise_type=compromise_type,
        evidence_digest=EVIDENCE_DIGEST,
        detected_at=detected_at,
        effective_at=effective_at,
        recorded_at=recorded_at,
        reported_by="OBSERVATORY-INSTITUTE",
        description="Private-key exposure was independently observed.",
        confirmed=True,
        historical_signatures_invalidated=(
            historical_signatures_invalidated
        ),
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_event() -> None:
    event = make_event()

    assert KeyCompromiseEventValidator().validate(event) is True


def test_event_is_immutable() -> None:
    event = make_event()

    with pytest.raises((AttributeError, TypeError)):
        event.confirmed = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "event_id",
        "key_id",
        "material_id",
        "owner_id",
        "issuer_id",
        "compromise_type",
        "reported_by",
        "description",
    ],
)
def test_event_rejects_empty_identity_or_description(
    field_name: str,
) -> None:
    arguments = {
        "event_id": "KCE-001",
        "key_id": "KEY-001",
        "material_id": "PKM-001",
        "public_key_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "compromise_type": "PRIVATE_KEY_EXPOSURE",
        "evidence_digest": EVIDENCE_DIGEST,
        "detected_at": DETECTED_AT,
        "effective_at": EFFECTIVE_AT,
        "recorded_at": RECORDED_AT,
        "reported_by": "OBSERVATORY-INSTITUTE",
        "description": (
            "Private-key exposure was independently observed."
        ),
        "confirmed": True,
        "historical_signatures_invalidated": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    arguments[field_name] = ""

    with pytest.raises(ValueError, match=field_name):
        KeyCompromiseEvent(**arguments)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("public_key_fingerprint", "md5:invalid"),
        ("evidence_digest", "sha256:abc"),
    ],
)
def test_event_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {
        "event_id": "KCE-001",
        "key_id": "KEY-001",
        "material_id": "PKM-001",
        "public_key_fingerprint": PUBLIC_KEY_FINGERPRINT,
        "owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "issuer_id": "OBSERVATORY-INSTITUTE",
        "compromise_type": "PRIVATE_KEY_EXPOSURE",
        "evidence_digest": EVIDENCE_DIGEST,
        "detected_at": DETECTED_AT,
        "effective_at": EFFECTIVE_AT,
        "recorded_at": RECORDED_AT,
        "reported_by": "OBSERVATORY-INSTITUTE",
        "description": (
            "Private-key exposure was independently observed."
        ),
        "confirmed": True,
        "historical_signatures_invalidated": False,
        "execution_requested": False,
        "side_effects_permitted": False,
    }
    arguments[field_name] = value

    with pytest.raises(ValueError, match=field_name):
        KeyCompromiseEvent(**arguments)


@pytest.mark.parametrize(
    "compromise_type",
    [
        "PRIVATE_KEY_EXPOSURE",
        "UNAUTHORIZED_KEY_USE",
        "KEY_MATERIAL_LOSS",
        "UNKNOWN_COMPROMISE",
    ],
)
def test_event_accepts_supported_compromise_type(
    compromise_type: str,
) -> None:
    event = make_event(compromise_type=compromise_type)

    assert event.compromise_type == compromise_type


def test_event_rejects_unsupported_compromise_type() -> None:
    with pytest.raises(ValueError, match="compromise_type"):
        make_event(compromise_type="OTHER")


@pytest.mark.parametrize(
    "field_name",
    [
        "detected_at",
        "effective_at",
        "recorded_at",
    ],
)
def test_event_rejects_naive_datetime(
    field_name: str,
) -> None:
    arguments = {
        "detected_at": DETECTED_AT,
        "effective_at": EFFECTIVE_AT,
        "recorded_at": RECORDED_AT,
    }
    arguments[field_name] = datetime(2026, 7, 15, 16, 0)

    with pytest.raises(
        ValueError,
        match=f"{field_name}.*timezone-aware",
    ):
        make_event(**arguments)


def test_event_rejects_detection_before_effective_time() -> None:
    with pytest.raises(
        ValueError,
        match="detected_at cannot be before effective_at",
    ):
        make_event(
            detected_at=datetime(
                2026,
                7,
                15,
                13,
                0,
                tzinfo=timezone.utc,
            ),
            effective_at=EFFECTIVE_AT,
        )


def test_event_rejects_recording_before_detection() -> None:
    with pytest.raises(
        ValueError,
        match="recorded_at cannot be before detected_at",
    ):
        make_event(
            recorded_at=datetime(
                2026,
                7,
                15,
                15,
                59,
                tzinfo=timezone.utc,
            )
        )


def test_event_rejects_non_boolean_confirmed() -> None:
    with pytest.raises(TypeError, match="confirmed"):
        event = make_event()
        object.__setattr__(event, "confirmed", "true")
        KeyCompromiseEventValidator().validate(event)


def test_event_rejects_unconfirmed_compromise() -> None:
    event = make_event()
    object.__setattr__(event, "confirmed", False)

    with pytest.raises(
        KeyCompromiseEventError,
        match="confirmed",
    ):
        KeyCompromiseEventValidator().validate(event)


def test_event_rejects_non_boolean_historical_invalidation() -> None:
    with pytest.raises(
        TypeError,
        match="historical_signatures_invalidated",
    ):
        KeyCompromiseEvent(
            event_id="KCE-001",
            key_id="KEY-001",
            material_id="PKM-001",
            public_key_fingerprint=PUBLIC_KEY_FINGERPRINT,
            owner_id="PROCESS-LINEAGE-CLASSIFIER",
            issuer_id="OBSERVATORY-INSTITUTE",
            compromise_type="PRIVATE_KEY_EXPOSURE",
            evidence_digest=EVIDENCE_DIGEST,
            detected_at=DETECTED_AT,
            effective_at=EFFECTIVE_AT,
            recorded_at=RECORDED_AT,
            reported_by="OBSERVATORY-INSTITUTE",
            description=(
                "Private-key exposure was independently observed."
            ),
            confirmed=True,
            historical_signatures_invalidated="false",  # type: ignore[arg-type]
            execution_requested=False,
            side_effects_permitted=False,
        )


def test_event_rejects_automatic_historical_invalidation() -> None:
    with pytest.raises(
        ValueError,
        match="must not automatically invalidate historical signatures",
    ):
        make_event(historical_signatures_invalidated=True)


def test_validator_rejects_non_event_input() -> None:
    with pytest.raises(TypeError, match="KeyCompromiseEvent"):
        KeyCompromiseEventValidator().validate(
            "KCE-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_references() -> None:
    event = make_event()

    assert KeyCompromiseEventValidator().validate(
        event,
        expected_key_id="KEY-001",
        expected_material_id="PKM-001",
        expected_owner_id="PROCESS-LINEAGE-CLASSIFIER",
        expected_issuer_id="OBSERVATORY-INSTITUTE",
        expected_fingerprint=PUBLIC_KEY_FINGERPRINT,
    ) is True


@pytest.mark.parametrize(
    ("field_name", "value", "error_match"),
    [
        ("expected_key_id", "KEY-999", "key identity"),
        (
            "expected_material_id",
            "PKM-999",
            "material identity",
        ),
        (
            "expected_owner_id",
            "OTHER-OWNER",
            "owner identity",
        ),
        (
            "expected_issuer_id",
            "OTHER-ISSUER",
            "issuer identity",
        ),
        (
            "expected_fingerprint",
            "sha256:" + ("9" * 64),
            "fingerprint",
        ),
    ],
)
def test_validator_rejects_reference_mismatch(
    field_name: str,
    value: str,
    error_match: str,
) -> None:
    arguments = {
        "expected_key_id": "KEY-001",
        "expected_material_id": "PKM-001",
        "expected_owner_id": "PROCESS-LINEAGE-CLASSIFIER",
        "expected_issuer_id": "OBSERVATORY-INSTITUTE",
        "expected_fingerprint": PUBLIC_KEY_FINGERPRINT,
    }
    arguments[field_name] = value

    with pytest.raises(
        KeyCompromiseEventError,
        match=error_match,
    ):
        KeyCompromiseEventValidator().validate(
            make_event(),
            **arguments,
        )


def test_validator_rejects_partial_expected_reference_set() -> None:
    with pytest.raises(
        KeyCompromiseEventError,
        match="complete expected reference set",
    ):
        KeyCompromiseEventValidator().validate(
            make_event(),
            expected_key_id="KEY-001",
        )


def test_validator_does_not_mutate_event() -> None:
    event = make_event()
    original = event

    KeyCompromiseEventValidator().validate(event)

    assert event == original


def test_event_preserves_non_retroactive_boundary() -> None:
    event = make_event()

    assert event.confirmed is True
    assert event.historical_signatures_invalidated is False


def test_event_preserves_observer_only_boundary() -> None:
    event = make_event()

    assert event.execution_requested is False
    assert event.side_effects_permitted is False