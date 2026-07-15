from dataclasses import dataclass
from datetime import datetime

from .audit_event_hash_link import AuditEventHashLink


@dataclass(frozen=True, slots=True)
class AuditHashChain:
    """Immutable observer-only chain of linked audit-event hashes."""

    chain_id: str
    subject_id: str
    links: tuple[AuditEventHashLink, ...]
    root_digest: str
    created_at: datetime
    issuer_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.chain_id, "chain_id")
        self._require_non_empty(self.subject_id, "subject_id")
        self._require_non_empty(self.issuer_id, "issuer_id")

        if not isinstance(self.links, tuple):
            raise TypeError("links must be a tuple.")

        if not self.links:
            raise ValueError(
                "links must contain at least one AuditEventHashLink."
            )

        if any(
            not isinstance(link, AuditEventHashLink)
            for link in self.links
        ):
            raise TypeError(
                "links must contain only AuditEventHashLink instances."
            )

        self._validate_unique_identities()
        self._validate_sequence_order()
        self._validate_digest(
            self.root_digest,
            "root_digest",
        )

        if self.root_digest != self.links[-1].current_digest:
            raise ValueError(
                "root digest must match the final link current digest."
            )

        if not isinstance(self.created_at, datetime):
            raise TypeError(
                "created_at must be a datetime."
            )

        if (
            self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise ValueError(
                "created_at must be timezone-aware."
            )

        if self.created_at < self.links[-1].linked_at:
            raise ValueError(
                "created_at cannot be before the final link timestamp."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "AuditHashChain must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "AuditHashChain must not permit side effects."
            )

    def _validate_unique_identities(self) -> None:
        link_ids = tuple(
            link.link_id
            for link in self.links
        )

        if len(set(link_ids)) != len(link_ids):
            raise ValueError(
                "duplicate link identity detected."
            )

        event_ids = tuple(
            link.event_id
            for link in self.links
        )

        if len(set(event_ids)) != len(event_ids):
            raise ValueError(
                "duplicate event identity detected."
            )

    def _validate_sequence_order(self) -> None:
        sequence_numbers = tuple(
            link.sequence_number
            for link in self.links
        )

        if (
            len(set(sequence_numbers))
            != len(sequence_numbers)
        ):
            raise ValueError(
                "duplicate sequence number detected."
            )

        if sequence_numbers != tuple(sorted(sequence_numbers)):
            raise ValueError(
                "Hash-link sequence numbers must be increasing."
            )

    @staticmethod
    def _validate_digest(
        digest: str,
        field_name: str,
    ) -> None:
        if not isinstance(digest, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not digest.startswith(prefix):
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise ValueError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise ValueError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be empty."
            )