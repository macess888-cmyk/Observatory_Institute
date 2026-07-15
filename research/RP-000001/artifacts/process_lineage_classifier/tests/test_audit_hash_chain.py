from datetime import datetime, timezone

import pytest

from models import AuditEventHashLink, AuditHashChain
from services.audit_hash_chain_validator import (
    AuditHashChainError,
    AuditHashChainValidator,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

GENESIS_DIGEST = "sha256:" + ("0" * 64)
DIGEST_001 = "sha256:" + ("1" * 64)
DIGEST_002 = "sha256:" + ("2" * 64)
DIGEST_003 = "sha256:" + ("3" * 64)


def make_link(
    *,
    link_id: str,
    event_id: str,
    sequence_number: int,
    previous_event_id: str | None,
    previous_digest: str,
    current_digest: str,
) -> AuditEventHashLink:
    return AuditEventHashLink(
        link_id=link_id,
        event_id=event_id,
        sequence_number=sequence_number,
        previous_event_id=previous_event_id,
        previous_digest=previous_digest,
        current_digest=current_digest,
        linked_at=CREATED_AT,
        linker_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_valid_links() -> tuple[AuditEventHashLink, ...]:
    return (
        make_link(
            link_id="AHL-001",
            event_id="AUD-001",
            sequence_number=1,
            previous_event_id=None,
            previous_digest=GENESIS_DIGEST,
            current_digest=DIGEST_001,
        ),
        make_link(
            link_id="AHL-002",
            event_id="AUD-002",
            sequence_number=2,
            previous_event_id="AUD-001",
            previous_digest=DIGEST_001,
            current_digest=DIGEST_002,
        ),
        make_link(
            link_id="AHL-003",
            event_id="AUD-003",
            sequence_number=3,
            previous_event_id="AUD-002",
            previous_digest=DIGEST_002,
            current_digest=DIGEST_003,
        ),
    )


def make_chain(
    *,
    chain_id: str = "AHC-001",
    subject_id: str = "RECOVERY-001",
    links: tuple[AuditEventHashLink, ...] | None = None,
    root_digest: str = DIGEST_003,
    created_at: datetime = CREATED_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> AuditHashChain:
    return AuditHashChain(
        chain_id=chain_id,
        subject_id=subject_id,
        links=make_valid_links() if links is None else links,
        root_digest=root_digest,
        created_at=created_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_valid_hash_chain() -> None:
    chain = make_chain()

    assert AuditHashChainValidator().validate(chain) is True


def test_chain_preserves_links() -> None:
    links = make_valid_links()
    chain = make_chain(links=links)

    assert chain.links == links
    assert chain.root_digest == links[-1].current_digest


def test_chain_is_immutable() -> None:
    chain = make_chain()

    with pytest.raises((AttributeError, TypeError)):
        chain.root_digest = DIGEST_001  # type: ignore[misc]


def test_chain_rejects_empty_chain_id() -> None:
    with pytest.raises(ValueError, match="chain_id"):
        make_chain(chain_id="")


def test_chain_rejects_empty_subject_id() -> None:
    with pytest.raises(ValueError, match="subject_id"):
        make_chain(subject_id="")


def test_chain_rejects_empty_issuer_id() -> None:
    with pytest.raises(ValueError, match="issuer_id"):
        make_chain(issuer_id="")


def test_chain_rejects_empty_link_set() -> None:
    with pytest.raises(ValueError, match="at least one"):
        make_chain(links=())


def test_chain_rejects_non_tuple_links() -> None:
    with pytest.raises(TypeError, match="tuple"):
        make_chain(
            links=list(make_valid_links()),  # type: ignore[arg-type]
        )


def test_chain_rejects_non_link_member() -> None:
    first, _, _ = make_valid_links()

    with pytest.raises(TypeError, match="AuditEventHashLink"):
        make_chain(
            links=(
                first,
                "AHL-002",
            ),  # type: ignore[arg-type]
        )


def test_chain_rejects_duplicate_link_identity() -> None:
    first, second, third = make_valid_links()

    duplicate = make_link(
        link_id=first.link_id,
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        previous_event_id=second.previous_event_id,
        previous_digest=second.previous_digest,
        current_digest=second.current_digest,
    )

    with pytest.raises(ValueError, match="duplicate link"):
        make_chain(links=(first, duplicate, third))


def test_chain_rejects_duplicate_event_identity() -> None:
    first, second, third = make_valid_links()

    duplicate = make_link(
        link_id=second.link_id,
        event_id=first.event_id,
        sequence_number=second.sequence_number,
        previous_event_id=second.previous_event_id,
        previous_digest=second.previous_digest,
        current_digest=second.current_digest,
    )

    with pytest.raises(ValueError, match="duplicate event"):
        make_chain(links=(first, duplicate, third))


def test_chain_rejects_duplicate_sequence_number() -> None:
    first, second, third = make_valid_links()

    duplicate = make_link(
        link_id=second.link_id,
        event_id=second.event_id,
        sequence_number=first.sequence_number,
        previous_event_id=None,
        previous_digest=GENESIS_DIGEST,
        current_digest=second.current_digest,
    )

    with pytest.raises(ValueError, match="duplicate sequence"):
        make_chain(links=(first, duplicate, third))


def test_chain_rejects_non_increasing_sequence() -> None:
    first, second, third = make_valid_links()

    reordered = (
        first,
        third,
        second,
    )

    with pytest.raises(ValueError, match="increasing"):
        make_chain(links=reordered)


def test_chain_rejects_root_digest_mismatch() -> None:
    with pytest.raises(ValueError, match="root digest"):
        make_chain(root_digest=DIGEST_001)


def test_chain_rejects_invalid_root_digest_prefix() -> None:
    with pytest.raises(ValueError, match="root_digest"):
        make_chain(root_digest="md5:invalid")


def test_chain_rejects_short_root_digest() -> None:
    with pytest.raises(ValueError, match="root_digest"):
        make_chain(root_digest="sha256:abc")


def test_chain_rejects_non_hex_root_digest() -> None:
    with pytest.raises(ValueError, match="root_digest"):
        make_chain(root_digest="sha256:" + ("z" * 64))


def test_chain_rejects_naive_created_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_chain(
            created_at=datetime(2026, 7, 15, 12, 0),
        )


def test_validator_rejects_non_chain_input() -> None:
    with pytest.raises(TypeError, match="AuditHashChain"):
        AuditHashChainValidator().validate(
            "AHC-001"  # type: ignore[arg-type]
        )


def test_validator_rejects_broken_previous_event_link() -> None:
    first, second, third = make_valid_links()

    broken = make_link(
        link_id=second.link_id,
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        previous_event_id="AUD-999",
        previous_digest=second.previous_digest,
        current_digest=second.current_digest,
    )

    chain = make_chain(links=(first, broken, third))

    with pytest.raises(
        AuditHashChainError,
        match="previous event identity",
    ):
        AuditHashChainValidator().validate(chain)


def test_validator_rejects_broken_previous_digest_link() -> None:
    first, second, third = make_valid_links()

    broken = make_link(
        link_id=second.link_id,
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        previous_event_id=second.previous_event_id,
        previous_digest="sha256:" + ("9" * 64),
        current_digest=second.current_digest,
    )

    chain = make_chain(links=(first, broken, third))

    with pytest.raises(
        AuditHashChainError,
        match="previous digest",
    ):
        AuditHashChainValidator().validate(chain)


def test_validator_rejects_non_contiguous_sequence() -> None:
    first = make_link(
        link_id="AHL-001",
        event_id="AUD-001",
        sequence_number=1,
        previous_event_id=None,
        previous_digest=GENESIS_DIGEST,
        current_digest=DIGEST_001,
    )
    second = make_link(
        link_id="AHL-002",
        event_id="AUD-002",
        sequence_number=3,
        previous_event_id="AUD-001",
        previous_digest=DIGEST_001,
        current_digest=DIGEST_002,
    )

    chain = make_chain(
        links=(first, second),
        root_digest=DIGEST_002,
    )

    with pytest.raises(
        AuditHashChainError,
        match="contiguous",
    ):
        AuditHashChainValidator().validate(chain)


def test_validator_rejects_linker_identity_mismatch() -> None:
    first, second, third = make_valid_links()

    mismatched = AuditEventHashLink(
        link_id=second.link_id,
        event_id=second.event_id,
        sequence_number=second.sequence_number,
        previous_event_id=second.previous_event_id,
        previous_digest=second.previous_digest,
        current_digest=second.current_digest,
        linked_at=second.linked_at,
        linker_id="OTHER-LINKER",
        execution_requested=False,
        side_effects_permitted=False,
    )

    chain = make_chain(links=(first, mismatched, third))

    with pytest.raises(
        AuditHashChainError,
        match="linker",
    ):
        AuditHashChainValidator().validate(chain)


def test_validator_rejects_linker_and_issuer_mismatch() -> None:
    chain = make_chain(issuer_id="OTHER-ISSUER")

    with pytest.raises(
        AuditHashChainError,
        match="issuer",
    ):
        AuditHashChainValidator().validate(chain)


def test_validator_does_not_mutate_chain() -> None:
    chain = make_chain()
    original = chain

    AuditHashChainValidator().validate(chain)

    assert chain == original


def test_chain_preserves_observer_only_boundary() -> None:
    chain = make_chain()

    assert chain.execution_requested is False
    assert chain.side_effects_permitted is False