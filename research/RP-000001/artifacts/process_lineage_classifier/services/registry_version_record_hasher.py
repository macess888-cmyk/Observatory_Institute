import hashlib
import json
from collections import OrderedDict

from models import RegistryVersionRecord


class RegistryVersionRecordHashError(ValueError):
    """Raised when registry-version record hashing fails."""


class RegistryVersionRecordHasher:
    """Canonicalizes, hashes, and validates registry-version records."""

    def canonicalize(
        self,
        record: RegistryVersionRecord,
    ) -> bytes:
        if not isinstance(record, RegistryVersionRecord):
            raise TypeError(
                "record must be a RegistryVersionRecord."
            )

        payload = OrderedDict(
            (
                ("record_id", record.record_id),
                ("registry_id", record.registry_id),
                (
                    "registry_version",
                    record.registry_version,
                ),
                (
                    "previous_registry_version",
                    record.previous_registry_version,
                ),
                ("snapshot_id", record.snapshot_id),
                ("snapshot_digest", record.snapshot_digest),
                (
                    "previous_snapshot_id",
                    record.previous_snapshot_id,
                ),
                (
                    "previous_snapshot_digest",
                    record.previous_snapshot_digest,
                ),
                (
                    "transition_type",
                    record.transition_type,
                ),
                (
                    "transition_receipt_id",
                    record.transition_receipt_id,
                ),
                (
                    "transition_receipt_digest",
                    record.transition_receipt_digest,
                ),
                (
                    "recorded_at",
                    record.recorded_at.isoformat(),
                ),
                ("owner_id", record.owner_id),
                ("issuer_id", record.issuer_id),
                (
                    "execution_requested",
                    record.execution_requested,
                ),
                (
                    "side_effects_permitted",
                    record.side_effects_permitted,
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
        record: RegistryVersionRecord,
    ) -> str:
        canonical = self.canonicalize(record)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        record: RegistryVersionRecord,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(record)

        if actual_digest != expected_digest:
            raise RegistryVersionRecordHashError(
                "Registry-version record hash mismatch."
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
            raise RegistryVersionRecordHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise RegistryVersionRecordHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise RegistryVersionRecordHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )