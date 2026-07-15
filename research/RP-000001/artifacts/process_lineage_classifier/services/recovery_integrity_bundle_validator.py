from models import RecoveryIntegrityBundle


class RecoveryIntegrityBundleError(ValueError):
    """Raised when a recovery integrity bundle fails validation."""


class RecoveryIntegrityBundleValidator:
    """Validates recovery integrity bundle identities and digests."""

    def validate(
        self,
        bundle: RecoveryIntegrityBundle,
        *,
        expected_subject_id: str | None = None,
        expected_decision_id: str | None = None,
        expected_reconciliation_receipt_id: str | None = None,
        expected_reconciliation_receipt_digest: str | None = None,
        expected_audit_chain_id: str | None = None,
        expected_audit_root_digest: str | None = None,
        expected_replay_manifest_id: str | None = None,
        expected_replay_manifest_digest: str | None = None,
        expected_verification_receipt_id: str | None = None,
        expected_verification_receipt_digest: str | None = None,
        expected_policy_binding_id: str | None = None,
        expected_policy_digest: str | None = None,
    ) -> bool:
        if not isinstance(bundle, RecoveryIntegrityBundle):
            raise TypeError(
                "bundle must be a RecoveryIntegrityBundle."
            )

        expected_values = (
            expected_subject_id,
            expected_decision_id,
            expected_reconciliation_receipt_id,
            expected_reconciliation_receipt_digest,
            expected_audit_chain_id,
            expected_audit_root_digest,
            expected_replay_manifest_id,
            expected_replay_manifest_digest,
            expected_verification_receipt_id,
            expected_verification_receipt_digest,
            expected_policy_binding_id,
            expected_policy_digest,
        )

        if all(value is None for value in expected_values):
            return True

        self._validate_expected_inputs(
            expected_subject_id=expected_subject_id,
            expected_decision_id=expected_decision_id,
            expected_reconciliation_receipt_id=(
                expected_reconciliation_receipt_id
            ),
            expected_reconciliation_receipt_digest=(
                expected_reconciliation_receipt_digest
            ),
            expected_audit_chain_id=expected_audit_chain_id,
            expected_audit_root_digest=expected_audit_root_digest,
            expected_replay_manifest_id=expected_replay_manifest_id,
            expected_replay_manifest_digest=(
                expected_replay_manifest_digest
            ),
            expected_verification_receipt_id=(
                expected_verification_receipt_id
            ),
            expected_verification_receipt_digest=(
                expected_verification_receipt_digest
            ),
            expected_policy_binding_id=expected_policy_binding_id,
            expected_policy_digest=expected_policy_digest,
        )

        comparisons = (
            (
                bundle.subject_id,
                expected_subject_id,
                "subject identity",
            ),
            (
                bundle.original_decision_id,
                expected_decision_id,
                "decision identity",
            ),
            (
                bundle.reconciliation_receipt_id,
                expected_reconciliation_receipt_id,
                "reconciliation receipt identity",
            ),
            (
                bundle.reconciliation_receipt_digest,
                expected_reconciliation_receipt_digest,
                "reconciliation receipt digest",
            ),
            (
                bundle.audit_chain_id,
                expected_audit_chain_id,
                "audit chain identity",
            ),
            (
                bundle.audit_root_digest,
                expected_audit_root_digest,
                "audit root digest",
            ),
            (
                bundle.replay_manifest_id,
                expected_replay_manifest_id,
                "replay manifest identity",
            ),
            (
                bundle.replay_manifest_digest,
                expected_replay_manifest_digest,
                "replay manifest digest",
            ),
            (
                bundle.verification_receipt_id,
                expected_verification_receipt_id,
                "verification receipt identity",
            ),
            (
                bundle.verification_receipt_digest,
                expected_verification_receipt_digest,
                "verification receipt digest",
            ),
            (
                bundle.policy_binding_id,
                expected_policy_binding_id,
                "policy binding identity",
            ),
            (
                bundle.policy_digest,
                expected_policy_digest,
                "policy digest",
            ),
        )

        for actual, expected, label in comparisons:
            if actual != expected:
                raise RecoveryIntegrityBundleError(
                    f"Recovery integrity bundle contains a {label} mismatch."
                )

        return True

    @classmethod
    def _validate_expected_inputs(
        cls,
        *,
        expected_subject_id: str | None,
        expected_decision_id: str | None,
        expected_reconciliation_receipt_id: str | None,
        expected_reconciliation_receipt_digest: str | None,
        expected_audit_chain_id: str | None,
        expected_audit_root_digest: str | None,
        expected_replay_manifest_id: str | None,
        expected_replay_manifest_digest: str | None,
        expected_verification_receipt_id: str | None,
        expected_verification_receipt_digest: str | None,
        expected_policy_binding_id: str | None,
        expected_policy_digest: str | None,
    ) -> None:
        for field_name, value in (
            ("expected_subject_id", expected_subject_id),
            ("expected_decision_id", expected_decision_id),
            (
                "expected_reconciliation_receipt_id",
                expected_reconciliation_receipt_id,
            ),
            (
                "expected_audit_chain_id",
                expected_audit_chain_id,
            ),
            (
                "expected_replay_manifest_id",
                expected_replay_manifest_id,
            ),
            (
                "expected_verification_receipt_id",
                expected_verification_receipt_id,
            ),
            (
                "expected_policy_binding_id",
                expected_policy_binding_id,
            ),
        ):
            cls._require_non_empty(value, field_name)

        for field_name, value in (
            (
                "expected_reconciliation_receipt_digest",
                expected_reconciliation_receipt_digest,
            ),
            (
                "expected_audit_root_digest",
                expected_audit_root_digest,
            ),
            (
                "expected_replay_manifest_digest",
                expected_replay_manifest_digest,
            ),
            (
                "expected_verification_receipt_digest",
                expected_verification_receipt_digest,
            ),
            (
                "expected_policy_digest",
                expected_policy_digest,
            ),
        ):
            cls._require_digest(value, field_name)

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