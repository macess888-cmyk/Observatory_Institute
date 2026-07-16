import hashlib
import json
from collections import OrderedDict

from models import KeyCompromiseEvent


class KeyCompromiseEventHashError(ValueError):
    """Raised when key-compromise event hashing fails."""


class KeyCompromiseEventHasher:
    """Canonicalizes, hashes, and validates key-compromise events."""

    def canonicalize(
        self,
        event: KeyCompromiseEvent,
    ) -> bytes:
        if not isinstance(event, KeyCompromiseEvent):
            raise TypeError(
                "event must be a KeyCompromiseEvent."
            )

        payload = OrderedDict(
            (
                ("event_id", event.event_id),
                ("key_id", event.key_id),
                ("material_id", event.material_id),
                (
                    "public_key_fingerprint",
                    event.public_key_fingerprint,
                ),
                ("owner_id", event.owner_id),
                ("issuer_id", event.issuer_id),
                (
                    "compromise_type",
                    event.compromise_type,
                ),
                (
                    "evidence_digest",
                    event.evidence_digest,
                ),
                (
                    "detected_at",
                    event.detected_at.isoformat(),
                ),
                (
                    "effective_at",
                    event.effective_at.isoformat(),
                ),
                (
                    "recorded_at",
                    event.recorded_at.isoformat(),
                ),
                ("reported_by", event.reported_by),
                ("description", event.description),
                ("confirmed", event.confirmed),
                (
                    "historical_signatures_invalidated",
                    event.historical_signatures_invalidated,
                ),
                (
                    "execution_requested",
                    event.execution_requested,
                ),
                (
                    "side_effects_permitted",
                    event.side_effects_permitted,
                ),
            )
        )

        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        return serialized.encode("utf-8")

    def hash(
        self,
        event: KeyCompromiseEvent,
    ) -> str:
        canonical = self.canonicalize(event)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        event: KeyCompromiseEvent,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(event)

        if actual_digest != expected_digest:
            raise KeyCompromiseEventHashError(
                "Key-compromise event hash mismatch."
            )

        return True

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
            raise KeyCompromiseEventHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise KeyCompromiseEventHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise KeyCompromiseEventHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )