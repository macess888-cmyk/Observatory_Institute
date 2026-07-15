from models import ReplayInputManifest


class ReplayInputManifestError(ValueError):
    """Raised when a replay input manifest fails validation."""


class ReplayInputManifestValidator:
    """Validates replay manifest integrity references."""

    def validate(
        self,
        manifest: ReplayInputManifest,
        *,
        expected_receipt_id: str | None = None,
        expected_receipt_digest: str | None = None,
        expected_audit_chain_id: str | None = None,
        expected_audit_root_digest: str | None = None,
        expected_policy_binding_id: str | None = None,
        expected_policy_digest: str | None = None,
    ) -> bool:
        if not isinstance(manifest, ReplayInputManifest):
            raise TypeError(
                "manifest must be a ReplayInputManifest."
            )

        expected_values = (
            expected_receipt_id,
            expected_receipt_digest,
            expected_audit_chain_id,
            expected_audit_root_digest,
            expected_policy_binding_id,
            expected_policy_digest,
        )

        if all(value is None for value in expected_values):
            return True

        self._require_non_empty(
            expected_receipt_id,
            "expected_receipt_id",
        )
        self._require_digest(
            expected_receipt_digest,
            "expected_receipt_digest",
        )
        self._require_non_empty(
            expected_audit_chain_id,
            "expected_audit_chain_id",
        )
        self._require_digest(
            expected_audit_root_digest,
            "expected_audit_root_digest",
        )
        self._require_non_empty(
            expected_policy_binding_id,
            "expected_policy_binding_id",
        )
        self._require_digest(
            expected_policy_digest,
            "expected_policy_digest",
        )

        if manifest.receipt_id != expected_receipt_id:
            raise ReplayInputManifestError(
                "Replay manifest contains a receipt identity mismatch."
            )

        if manifest.receipt_digest != expected_receipt_digest:
            raise ReplayInputManifestError(
                "Replay manifest contains a receipt digest mismatch."
            )

        if manifest.audit_chain_id != expected_audit_chain_id:
            raise ReplayInputManifestError(
                "Replay manifest contains an audit chain identity mismatch."
            )

        if manifest.audit_root_digest != expected_audit_root_digest:
            raise ReplayInputManifestError(
                "Replay manifest contains an audit root digest mismatch."
            )

        if manifest.policy_binding_id != expected_policy_binding_id:
            raise ReplayInputManifestError(
                "Replay manifest contains a policy binding identity "
                "mismatch."
            )

        if manifest.policy_digest != expected_policy_digest:
            raise ReplayInputManifestError(
                "Replay manifest contains a policy digest mismatch."
            )

        return True

    @staticmethod
    def _require_non_empty(
        value: str | None,
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

    @staticmethod
    def _require_digest(
        value: str | None,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not value.startswith(prefix):
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = value.removeprefix(prefix)

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