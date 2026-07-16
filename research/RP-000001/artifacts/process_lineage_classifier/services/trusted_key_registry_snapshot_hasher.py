import hashlib
import json
from collections import OrderedDict

from models import TrustedKeyRegistrySnapshot


class TrustedKeyRegistrySnapshotHashError(ValueError):
    """Raised when trusted-key registry snapshot hashing fails."""


class TrustedKeyRegistrySnapshotHasher:
    """Canonicalizes, hashes, and validates registry snapshots."""

    def canonicalize(
        self,
        snapshot: TrustedKeyRegistrySnapshot,
    ) -> bytes:
        if not isinstance(
            snapshot,
            TrustedKeyRegistrySnapshot,
        ):
            raise TypeError(
                "snapshot must be a TrustedKeyRegistrySnapshot."
            )

        materials = [
            OrderedDict(
                (
                    ("material_id", material.material_id),
                    ("key_id", material.key_id),
                    ("owner_id", material.owner_id),
                    ("algorithm", material.algorithm),
                    ("encoding", material.encoding),
                    (
                        "public_key_value",
                        material.public_key_value,
                    ),
                    (
                        "public_key_fingerprint",
                        material.public_key_fingerprint,
                    ),
                    (
                        "created_at",
                        material.created_at.isoformat(),
                    ),
                    (
                        "valid_from",
                        material.valid_from.isoformat(),
                    ),
                    (
                        "valid_until",
                        material.valid_until.isoformat(),
                    ),
                    ("issuer_id", material.issuer_id),
                    ("revoked", material.revoked),
                    (
                        "execution_requested",
                        material.execution_requested,
                    ),
                    (
                        "side_effects_permitted",
                        material.side_effects_permitted,
                    ),
                )
            )
            for material in snapshot.materials
        ]

        payload = OrderedDict(
            (
                ("snapshot_id", snapshot.snapshot_id),
                ("registry_id", snapshot.registry_id),
                (
                    "registry_version",
                    snapshot.registry_version,
                ),
                ("materials", materials),
                (
                    "captured_at",
                    snapshot.captured_at.isoformat(),
                ),
                ("owner_id", snapshot.owner_id),
                ("issuer_id", snapshot.issuer_id),
                (
                    "execution_requested",
                    snapshot.execution_requested,
                ),
                (
                    "side_effects_permitted",
                    snapshot.side_effects_permitted,
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
        snapshot: TrustedKeyRegistrySnapshot,
    ) -> str:
        canonical = self.canonicalize(snapshot)
        digest = hashlib.sha256(canonical).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        snapshot: TrustedKeyRegistrySnapshot,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.hash(snapshot)

        if actual_digest != expected_digest:
            raise TrustedKeyRegistrySnapshotHashError(
                "Trusted-key registry snapshot hash mismatch."
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
            raise TrustedKeyRegistrySnapshotHashError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise TrustedKeyRegistrySnapshotHashError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise TrustedKeyRegistrySnapshotHashError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )