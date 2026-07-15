from models import AuditEventHashLink


class AuditEventHashLinkError(ValueError):
    """Raised when an audit-event hash link fails validation."""


class AuditEventHashLinkValidator:
    """Validates cryptographic continuity between audit-event hash links."""

    def validate(
        self,
        link: AuditEventHashLink,
        *,
        expected_previous_event_id: str | None = None,
        expected_previous_digest: str | None = None,
    ) -> bool:
        if not isinstance(link, AuditEventHashLink):
            raise TypeError(
                "link must be an AuditEventHashLink."
            )

        if link.sequence_number == 1:
            if (
                expected_previous_event_id is not None
                or expected_previous_digest is not None
            ):
                raise AuditEventHashLinkError(
                    "Genesis link cannot be validated against previous "
                    "event data."
                )

            return True

        self._require_expected_previous_event_id(
            expected_previous_event_id
        )
        self._require_expected_previous_digest(
            expected_previous_digest
        )

        if link.previous_event_id != expected_previous_event_id:
            raise AuditEventHashLinkError(
                "Audit link contains a previous event identity mismatch."
            )

        if link.previous_digest != expected_previous_digest:
            raise AuditEventHashLinkError(
                "Audit link contains a previous digest mismatch."
            )

        return True

    @staticmethod
    def _require_expected_previous_event_id(
        value: str | None,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                "expected_previous_event_id must be a string."
            )

        if not value.strip():
            raise ValueError(
                "expected_previous_event_id must not be empty."
            )

    @staticmethod
    def _require_expected_previous_digest(
        value: str | None,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                "expected_previous_digest must be a string."
            )

        prefix = "sha256:"

        if not value.startswith(prefix):
            raise ValueError(
                "expected_previous_digest must use the sha256 prefix."
            )

        digest_value = value.removeprefix(prefix)

        if len(digest_value) != 64:
            raise ValueError(
                "expected_previous_digest must contain 64 hexadecimal "
                "characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise ValueError(
                "expected_previous_digest must contain only lowercase "
                "hexadecimal characters."
            )