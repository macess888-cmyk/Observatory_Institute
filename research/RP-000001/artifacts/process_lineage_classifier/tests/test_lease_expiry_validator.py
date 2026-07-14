from datetime import datetime, timedelta, timezone

import pytest

from enums import EventType
from models import ProcessEvent
from services.lease_expiry_validator import (
    ExpiredLeaseError,
    InvalidLeaseError,
    LeaseExpiryValidator,
    LeaseNotYetActiveError,
)


REFERENCE_TIME = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_event(
    *,
    event_id: str = "EV-001",
    sequence_number: int = 1,
    timestamp: datetime = REFERENCE_TIME,
    authority_role: str = "PRIMARY",
) -> ProcessEvent:
    return ProcessEvent(
        event_id=event_id,
        event_type=EventType.START,
        timestamp=timestamp,
        sequence_number=sequence_number,
        service_id="SERVICE-A",
        runtime_id="RUNTIME-A",
        execution_id="EXEC-A",
        state_id="STATE-100",
        host_id="HOST-A",
        address="10.0.0.10",
        authority_role=authority_role,
    )


def test_validator_accepts_active_lease() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=2),
        lease_expires_at=REFERENCE_TIME + timedelta(minutes=3),
    )

    assert validator.validate(event, now=REFERENCE_TIME) is True


def test_validator_accepts_lease_at_start_boundary() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME,
        lease_expires_at=REFERENCE_TIME + timedelta(minutes=5),
    )

    assert validator.validate(event, now=REFERENCE_TIME) is True


def test_validator_accepts_lease_before_expiry_boundary() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=5),
        lease_expires_at=REFERENCE_TIME + timedelta(microseconds=1),
    )

    assert validator.validate(event, now=REFERENCE_TIME) is True


def test_validator_rejects_expired_lease_at_boundary() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=5),
        lease_expires_at=REFERENCE_TIME,
    )

    with pytest.raises(ExpiredLeaseError, match="expired"):
        validator.validate(event, now=REFERENCE_TIME)


def test_validator_rejects_expired_lease_after_boundary() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=10),
        lease_expires_at=REFERENCE_TIME - timedelta(seconds=1),
    )

    with pytest.raises(ExpiredLeaseError, match="expired"):
        validator.validate(event, now=REFERENCE_TIME)


def test_validator_rejects_lease_not_yet_active() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME + timedelta(seconds=1),
        lease_expires_at=REFERENCE_TIME + timedelta(minutes=5),
    )

    with pytest.raises(LeaseNotYetActiveError, match="not yet active"):
        validator.validate(event, now=REFERENCE_TIME)


def test_validator_rejects_end_before_start() -> None:
    with pytest.raises(InvalidLeaseError, match="after"):
        LeaseExpiryValidator(
            lease_started_at=REFERENCE_TIME,
            lease_expires_at=REFERENCE_TIME - timedelta(seconds=1),
        )


def test_validator_rejects_equal_start_and_end() -> None:
    with pytest.raises(InvalidLeaseError, match="after"):
        LeaseExpiryValidator(
            lease_started_at=REFERENCE_TIME,
            lease_expires_at=REFERENCE_TIME,
        )


def test_validator_rejects_naive_start_time() -> None:
    with pytest.raises(TypeError, match="timezone-aware"):
        LeaseExpiryValidator(
            lease_started_at=datetime(2026, 7, 14, 11, 0),
            lease_expires_at=REFERENCE_TIME + timedelta(minutes=5),
        )


def test_validator_rejects_naive_expiry_time() -> None:
    with pytest.raises(TypeError, match="timezone-aware"):
        LeaseExpiryValidator(
            lease_started_at=REFERENCE_TIME - timedelta(minutes=5),
            lease_expires_at=datetime(2026, 7, 14, 12, 5),
        )


def test_validator_rejects_naive_reference_time() -> None:
    event = make_event()

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=5),
        lease_expires_at=REFERENCE_TIME + timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="timezone-aware"):
        validator.validate(
            event,
            now=datetime(2026, 7, 14, 12, 0),
        )


def test_validator_requires_process_event_input() -> None:
    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=5),
        lease_expires_at=REFERENCE_TIME + timedelta(minutes=5),
    )

    with pytest.raises(TypeError, match="ProcessEvent"):
        validator.validate(
            "EV-001",  # type: ignore[arg-type]
            now=REFERENCE_TIME,
        )


def test_validator_rejects_primary_authority_after_expiry() -> None:
    event = make_event(authority_role="PRIMARY")

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=10),
        lease_expires_at=REFERENCE_TIME - timedelta(seconds=1),
    )

    with pytest.raises(ExpiredLeaseError, match="authority"):
        validator.validate(event, now=REFERENCE_TIME)


def test_validator_allows_non_authoritative_event_check_before_expiry() -> None:
    event = make_event(authority_role="NONE")

    validator = LeaseExpiryValidator(
        lease_started_at=REFERENCE_TIME - timedelta(minutes=2),
        lease_expires_at=REFERENCE_TIME + timedelta(minutes=2),
    )

    assert validator.validate(event, now=REFERENCE_TIME) is True