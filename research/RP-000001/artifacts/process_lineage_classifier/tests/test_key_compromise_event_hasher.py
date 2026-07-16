import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import KeyCompromiseEvent
from services.key_compromise_event_hasher import (
    KeyCompromiseEventHashError,
    KeyCompromiseEventHasher,
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
    reported_by: str = "OBSERVATORY-INSTITUTE",
    description: str = (
        "Private-key exposure was independently observed."
    ),
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
        detected_at=DETECTED_AT,
        effective_at=EFFECTIVE_AT,
        recorded_at=RECORDED_AT,
        reported_by=reported_by,
        description=description,
        confirmed=True,
        historical_signatures_invalidated=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_hasher_generates_expected_digest() -> None:
    event = make_event()
    hasher = KeyCompromiseEventHasher()
    canonical = hasher.canonicalize(event)
    expected = "sha256:" + hashlib.sha256(canonical).hexdigest()
    assert hasher.hash(event) == expected


def test_canonicalization_returns_bytes() -> None:
    assert isinstance(
        KeyCompromiseEventHasher().canonicalize(make_event()),
        bytes,
    )


def test_hashing_is_deterministic() -> None:
    hasher = KeyCompromiseEventHasher()
    event = make_event()
    assert hasher.hash(event) == hasher.hash(event)


def test_equivalent_events_produce_same_hash() -> None:
    hasher = KeyCompromiseEventHasher()
    assert hasher.hash(make_event()) == hasher.hash(make_event())


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("event_id", "KCE-999"),
        ("key_id", "KEY-999"),
        ("material_id", "PKM-999"),
        ("compromise_type", "UNAUTHORIZED_KEY_USE"),
        ("reported_by", "OTHER-REPORTER"),
        ("description", "Different compromise evidence."),
    ],
)
def test_changed_field_changes_hash(
    field_name: str,
    value: str,
) -> None:
    hasher = KeyCompromiseEventHasher()
    baseline = hasher.hash(make_event())
    changed = hasher.hash(make_event(**{field_name: value}))
    assert baseline != changed


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        (
            "effective_at",
            datetime(2026, 7, 15, 13, 31, tzinfo=timezone.utc),
        ),
        (
            "detected_at",
            datetime(2026, 7, 15, 16, 1, tzinfo=timezone.utc),
        ),
        (
            "recorded_at",
            datetime(2026, 7, 15, 16, 6, tzinfo=timezone.utc),
        ),
    ],
)
def test_changed_time_changes_hash(
    field_name: str,
    value: datetime,
) -> None:
    hasher = KeyCompromiseEventHasher()
    baseline = make_event()
    changed = make_event()
    object.__setattr__(changed, field_name, value)
    assert hasher.hash(baseline) != hasher.hash(changed)


def test_canonical_payload_has_no_extra_whitespace() -> None:
    text = (
        KeyCompromiseEventHasher()
        .canonicalize(make_event())
        .decode("utf-8")
    )
    assert ": " not in text
    assert ", " not in text
    assert "\n" not in text


def test_canonical_payload_uses_expected_field_order() -> None:
    canonical = KeyCompromiseEventHasher().canonicalize(make_event())
    decoded = json.loads(
        canonical.decode("utf-8"),
        object_pairs_hook=dict,
    )
    assert tuple(decoded.keys()) == (
        "event_id",
        "key_id",
        "material_id",
        "public_key_fingerprint",
        "owner_id",
        "issuer_id",
        "compromise_type",
        "evidence_digest",
        "detected_at",
        "effective_at",
        "recorded_at",
        "reported_by",
        "description",
        "confirmed",
        "historical_signatures_invalidated",
        "execution_requested",
        "side_effects_permitted",
    )


def test_canonical_payload_uses_iso_timestamps() -> None:
    text = (
        KeyCompromiseEventHasher()
        .canonicalize(make_event())
        .decode("utf-8")
    )
    assert DETECTED_AT.isoformat() in text
    assert EFFECTIVE_AT.isoformat() in text
    assert RECORDED_AT.isoformat() in text


def test_canonical_payload_is_valid_json() -> None:
    canonical = KeyCompromiseEventHasher().canonicalize(make_event())
    decoded = json.loads(canonical.decode("utf-8"))
    assert decoded["event_id"] == "KCE-001"
    assert decoded["confirmed"] is True
    assert decoded["historical_signatures_invalidated"] is False
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_hasher_rejects_non_event_input() -> None:
    with pytest.raises(TypeError, match="KeyCompromiseEvent"):
        KeyCompromiseEventHasher().hash(
            "KCE-001"  # type: ignore[arg-type]
        )


def test_canonicalizer_rejects_non_event_input() -> None:
    with pytest.raises(TypeError, match="KeyCompromiseEvent"):
        KeyCompromiseEventHasher().canonicalize(
            "KCE-001"  # type: ignore[arg-type]
        )


def test_validate_accepts_matching_digest() -> None:
    hasher = KeyCompromiseEventHasher()
    event = make_event()
    assert hasher.validate(event, hasher.hash(event)) is True


def test_validate_rejects_hash_mismatch() -> None:
    with pytest.raises(
        KeyCompromiseEventHashError,
        match="hash mismatch",
    ):
        KeyCompromiseEventHasher().validate(
            make_event(),
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
        KeyCompromiseEventHashError,
        match="expected_digest",
    ):
        KeyCompromiseEventHasher().validate(make_event(), digest)


def test_hasher_does_not_mutate_event() -> None:
    event = make_event()
    original = event
    KeyCompromiseEventHasher().hash(event)
    assert event == original


def test_hash_preserves_non_retroactive_boundary() -> None:
    canonical = KeyCompromiseEventHasher().canonicalize(make_event())
    decoded = json.loads(canonical.decode("utf-8"))
    assert decoded["confirmed"] is True
    assert decoded["historical_signatures_invalidated"] is False


def test_event_preserves_observer_only_boundary() -> None:
    event = make_event()
    assert event.execution_requested is False
    assert event.side_effects_permitted is False