from datetime import datetime, timezone

import pytest

from models import AuditEventHashLink
from services.audit_event_hash_link_validator import (
    AuditEventHashLinkError,
    AuditEventHashLinkValidator,
)


LINKED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

GENESIS_DIGEST = "sha256:" + ("0" * 64)
PREVIOUS_DIGEST = "sha256:" + ("1" * 64)
CURRENT_DIGEST = "sha256:" + ("2" * 64)


def make_link(
    *,
    link_id: str = "AHL-001",
    event_id: str = "AUD-001",
    sequence_number: int = 1,
    previous_event_id: str | None = None,
    previous_digest: str = GENESIS_DIGEST,
    current_digest: str = CURRENT_DIGEST,
    linked_at: datetime = LINKED_AT,
    linker_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> AuditEventHashLink:
    return AuditEventHashLink(
        link_id=link_id,
        event_id=event_id,
        sequence_number=sequence_number,
        previous_event_id=previous_event_id,
        previous_digest=previous_digest,
        current_digest=current_digest,
        linked_at=linked_at,
        linker_id=linker_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_genesis_link() -> None:
    assert AuditEventHashLinkValidator().validate(make_link()) is True


def test_validator_accepts_non_genesis_link() -> None:
    link = make_link(
        link_id="AHL-002",
        event_id="AUD-002",
        sequence_number=2,
        previous_event_id="AUD-001",
        previous_digest=PREVIOUS_DIGEST,
    )

    assert AuditEventHashLinkValidator().validate(
        link,
        expected_previous_event_id="AUD-001",
        expected_previous_digest=PREVIOUS_DIGEST,
    ) is True


def test_link_is_immutable() -> None:
    link = make_link()

    with pytest.raises((AttributeError, TypeError)):
        link.current_digest = PREVIOUS_DIGEST  # type: ignore[misc]


def test_link_rejects_empty_link_id() -> None:
    with pytest.raises(ValueError, match="link_id"):
        make_link(link_id="")


def test_link_rejects_empty_event_id() -> None:
    with pytest.raises(ValueError, match="event_id"):
        make_link(event_id="")


def test_link_rejects_zero_sequence_number() -> None:
    with pytest.raises(ValueError, match="sequence_number"):
        make_link(sequence_number=0)


def test_link_rejects_negative_sequence_number() -> None:
    with pytest.raises(ValueError, match="sequence_number"):
        make_link(sequence_number=-1)


def test_link_rejects_non_integer_sequence_number() -> None:
    with pytest.raises(TypeError, match="sequence_number"):
        make_link(sequence_number="1")  # type: ignore[arg-type]


def test_genesis_link_rejects_previous_event_identity() -> None:
    with pytest.raises(ValueError, match="genesis"):
        make_link(sequence_number=1, previous_event_id="AUD-000")


def test_genesis_link_requires_genesis_digest() -> None:
    with pytest.raises(ValueError, match="genesis digest"):
        make_link(sequence_number=1, previous_digest=PREVIOUS_DIGEST)


def test_non_genesis_link_requires_previous_event_identity() -> None:
    with pytest.raises(ValueError, match="previous_event_id"):
        make_link(
            sequence_number=2,
            previous_event_id=None,
            previous_digest=PREVIOUS_DIGEST,
        )


def test_non_genesis_link_rejects_genesis_digest() -> None:
    with pytest.raises(ValueError, match="genesis digest"):
        make_link(
            sequence_number=2,
            previous_event_id="AUD-001",
            previous_digest=GENESIS_DIGEST,
        )


def test_link_rejects_same_previous_and_current_digest() -> None:
    with pytest.raises(ValueError, match="different"):
        make_link(
            sequence_number=2,
            previous_event_id="AUD-001",
            previous_digest=CURRENT_DIGEST,
            current_digest=CURRENT_DIGEST,
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("previous_digest", "md5:invalid"),
        ("current_digest", "md5:invalid"),
        ("previous_digest", "sha256:abc"),
        ("current_digest", "sha256:abc"),
        ("previous_digest", "sha256:" + ("z" * 64)),
        ("current_digest", "sha256:" + ("z" * 64)),
    ],
)
def test_link_rejects_invalid_digest(
    field_name: str,
    value: str,
) -> None:
    arguments = {field_name: value}

    with pytest.raises(ValueError, match=field_name):
        make_link(**arguments)


def test_link_rejects_naive_linked_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_link(linked_at=datetime(2026, 7, 15, 12, 0))


def test_link_rejects_empty_linker_id() -> None:
    with pytest.raises(ValueError, match="linker_id"):
        make_link(linker_id="")


def test_validator_rejects_non_link_input() -> None:
    with pytest.raises(TypeError, match="AuditEventHashLink"):
        AuditEventHashLinkValidator().validate(
            "AHL-001"  # type: ignore[arg-type]
        )


def test_validator_accepts_expected_previous_event() -> None:
    link = make_link(
        link_id="AHL-002",
        event_id="AUD-002",
        sequence_number=2,
        previous_event_id="AUD-001",
        previous_digest=PREVIOUS_DIGEST,
    )

    assert AuditEventHashLinkValidator().validate(
        link,
        expected_previous_event_id="AUD-001",
        expected_previous_digest=PREVIOUS_DIGEST,
    ) is True


def test_validator_rejects_previous_event_identity_mismatch() -> None:
    link = make_link(
        link_id="AHL-002",
        event_id="AUD-002",
        sequence_number=2,
        previous_event_id="AUD-001",
        previous_digest=PREVIOUS_DIGEST,
    )

    with pytest.raises(
        AuditEventHashLinkError,
        match="previous event identity",
    ):
        AuditEventHashLinkValidator().validate(
            link,
            expected_previous_event_id="AUD-999",
            expected_previous_digest=PREVIOUS_DIGEST,
        )


def test_validator_rejects_previous_digest_mismatch() -> None:
    link = make_link(
        link_id="AHL-002",
        event_id="AUD-002",
        sequence_number=2,
        previous_event_id="AUD-001",
        previous_digest=PREVIOUS_DIGEST,
    )

    with pytest.raises(
        AuditEventHashLinkError,
        match="previous digest",
    ):
        AuditEventHashLinkValidator().validate(
            link,
            expected_previous_event_id="AUD-001",
            expected_previous_digest="sha256:" + ("3" * 64),
        )


def test_validator_rejects_expected_previous_data_for_genesis() -> None:
    with pytest.raises(AuditEventHashLinkError, match="Genesis"):
        AuditEventHashLinkValidator().validate(
            make_link(),
            expected_previous_event_id="AUD-000",
            expected_previous_digest=PREVIOUS_DIGEST,
        )


def test_link_preserves_observer_only_boundary() -> None:
    link = make_link()

    assert link.execution_requested is False
    assert link.side_effects_permitted is False