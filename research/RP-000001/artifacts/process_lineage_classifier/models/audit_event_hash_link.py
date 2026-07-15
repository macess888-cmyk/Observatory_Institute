from dataclasses import dataclass
from datetime import datetime


GENESIS_DIGEST = "sha256:" + ("0" * 64)


@dataclass(frozen=True, slots=True)
class AuditEventHashLink:
    """Immutable observer-only cryptographic link between audit events."""

    link_id: str
    event_id: str
    sequence_number: int
    previous_event_id: str | None
    previous_digest: str
    current_digest: str
    linked_at: datetime
    linker_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.link_id, "link_id")
        self._require_non_empty(self.event_id, "event_id")
        self._require_non_empty(self.linker_id, "linker_id")

        if not isinstance(self.sequence_number, int):
            raise TypeError(
                "sequence_number must be an integer."
            )

        if self.sequence_number < 1:
            raise ValueError(
                "sequence_number must be greater than zero."
            )

        if (
            self.previous_event_id is not None
            and not isinstance(self.previous_event_id, str)
        ):
            raise TypeError(
                "previous_event_id must be a string or None."
            )

        if (
            isinstance(self.previous_event_id, str)
            and not self.previous_event_id.strip()
        ):
            raise ValueError(
                "previous_event_id must not be empty."
            )

        self._validate_digest(
            self.previous_digest,
            "previous_digest",
        )
        self._validate_digest(
            self.current_digest,
            "current_digest",
        )

        self._validate_genesis_relationship()

        if self.previous_digest == self.current_digest:
            raise ValueError(
                "previous_digest and current_digest must be different."
            )

        if not isinstance(self.linked_at, datetime):
            raise TypeError(
                "linked_at must be a datetime."
            )

        if (
            self.linked_at.tzinfo is None
            or self.linked_at.utcoffset() is None
        ):
            raise ValueError(
                "linked_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "AuditEventHashLink must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "AuditEventHashLink must not permit side effects."
            )

    def _validate_genesis_relationship(self) -> None:
        if self.sequence_number == 1:
            if self.previous_event_id is not None:
                raise ValueError(
                    "A genesis link cannot contain a previous event identity."
                )

            if self.previous_digest != GENESIS_DIGEST:
                raise ValueError(
                    "A genesis link requires the genesis digest."
                )

            return

        if self.previous_event_id is None:
            raise ValueError(
                "A non-genesis link requires previous_event_id."
            )

        if self.previous_digest == GENESIS_DIGEST:
            raise ValueError(
                "A non-genesis link cannot use the genesis digest."
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