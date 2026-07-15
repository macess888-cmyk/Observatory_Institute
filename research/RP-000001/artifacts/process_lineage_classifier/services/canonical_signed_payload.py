import hashlib
import json
from collections import OrderedDict

from models import RecoveryIntegrityBundle


class CanonicalSignedPayloadError(ValueError):
    """Raised when canonical payload generation or digest validation fails."""


class CanonicalSignedPayloadService:
    """Generates deterministic signed payloads for recovery integrity bundles."""

    def generate(
        self,
        bundle: RecoveryIntegrityBundle,
    ) -> bytes:
        if not isinstance(
            bundle,
            RecoveryIntegrityBundle,
        ):
            raise TypeError(
                "bundle must be a RecoveryIntegrityBundle."
            )

        payload = OrderedDict(
            (
                ("bundle_id", bundle.bundle_id),
                ("subject_id", bundle.subject_id),
                (
                    "original_decision_id",
                    bundle.original_decision_id,
                ),
                (
                    "reconciliation_receipt_id",
                    bundle.reconciliation_receipt_id,
                ),
                (
                    "reconciliation_receipt_digest",
                    bundle.reconciliation_receipt_digest,
                ),
                (
                    "audit_chain_id",
                    bundle.audit_chain_id,
                ),
                (
                    "audit_root_digest",
                    bundle.audit_root_digest,
                ),
                (
                    "replay_manifest_id",
                    bundle.replay_manifest_id,
                ),
                (
                    "replay_manifest_digest",
                    bundle.replay_manifest_digest,
                ),
                (
                    "verification_receipt_id",
                    bundle.verification_receipt_id,
                ),
                (
                    "verification_receipt_digest",
                    bundle.verification_receipt_digest,
                ),
                (
                    "policy_binding_id",
                    bundle.policy_binding_id,
                ),
                (
                    "policy_digest",
                    bundle.policy_digest,
                ),
                (
                    "trust_provenance_ids",
                    list(bundle.trust_provenance_ids),
                ),
                (
                    "trust_digests",
                    list(bundle.trust_digests),
                ),
                (
                    "created_at",
                    bundle.created_at.isoformat(),
                ),
                (
                    "issuer_id",
                    bundle.issuer_id,
                ),
                (
                    "execution_requested",
                    bundle.execution_requested,
                ),
                (
                    "side_effects_permitted",
                    bundle.side_effects_permitted,
                ),
            )
        )

        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        return serialized.encode("utf-8")

    def digest(
        self,
        bundle: RecoveryIntegrityBundle,
    ) -> str:
        payload = self.generate(bundle)
        digest_value = hashlib.sha256(payload).hexdigest()

        return f"sha256:{digest_value}"

    def validate_digest(
        self,
        bundle: RecoveryIntegrityBundle,
        expected_digest: str,
    ) -> bool:
        self._validate_digest(
            expected_digest,
            "expected_digest",
        )

        actual_digest = self.digest(bundle)

        if actual_digest != expected_digest:
            raise CanonicalSignedPayloadError(
                "Canonical signed payload digest mismatch."
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
            raise CanonicalSignedPayloadError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise CanonicalSignedPayloadError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise CanonicalSignedPayloadError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )