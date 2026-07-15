from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RecoveryIntegrityBundle:
    """Immutable observer-only bundle of recovery integrity references."""

    bundle_id: str
    subject_id: str
    original_decision_id: str

    reconciliation_receipt_id: str
    reconciliation_receipt_digest: str

    audit_chain_id: str
    audit_root_digest: str

    replay_manifest_id: str
    replay_manifest_digest: str

    verification_receipt_id: str
    verification_receipt_digest: str

    policy_binding_id: str
    policy_digest: str

    trust_provenance_ids: tuple[str, ...]
    trust_digests: tuple[str, ...]

    created_at: datetime
    issuer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("bundle_id", self.bundle_id),
            ("subject_id", self.subject_id),
            ("original_decision_id", self.original_decision_id),
            (
                "reconciliation_receipt_id",
                self.reconciliation_receipt_id,
            ),
            ("audit_chain_id", self.audit_chain_id),
            ("replay_manifest_id", self.replay_manifest_id),
            (
                "verification_receipt_id",
                self.verification_receipt_id,
            ),
            ("policy_binding_id", self.policy_binding_id),
            ("issuer_id", self.issuer_id),
        ):
            self._require_non_empty(value, field_name)

        for field_name, digest in (
            (
                "reconciliation_receipt_digest",
                self.reconciliation_receipt_digest,
            ),
            ("audit_root_digest", self.audit_root_digest),
            (
                "replay_manifest_digest",
                self.replay_manifest_digest,
            ),
            (
                "verification_receipt_digest",
                self.verification_receipt_digest,
            ),
            ("policy_digest", self.policy_digest),
        ):
            self._validate_digest(digest, field_name)

        self._validate_identity_tuple(
            self.trust_provenance_ids,
            "trust_provenance_ids",
        )
        self._validate_digest_tuple(
            self.trust_digests,
            "trust_digests",
        )

        if not self.trust_provenance_ids:
            raise ValueError(
                "trust_provenance_ids must contain at least one identity."
            )

        if not self.trust_digests:
            raise ValueError(
                "trust_digests must contain at least one digest."
            )

        if (
            len(self.trust_provenance_ids)
            != len(self.trust_digests)
        ):
            raise ValueError(
                "trust provenance identities and digests must have "
                "matching counts."
            )

        if (
            len(set(self.trust_provenance_ids))
            != len(self.trust_provenance_ids)
        ):
            raise ValueError(
                "duplicate trust provenance identity detected."
            )

        if len(set(self.trust_digests)) != len(self.trust_digests):
            raise ValueError(
                "duplicate trust digest detected."
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

        if self.execution_requested is not False:
            raise ValueError(
                "RecoveryIntegrityBundle must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "RecoveryIntegrityBundle must not permit side effects."
            )

    @staticmethod
    def _validate_identity_tuple(
        values: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple."
            )

        if any(
            not isinstance(value, str)
            for value in values
        ):
            raise TypeError(
                f"{field_name} must contain only strings."
            )

        if any(
            not value.strip()
            for value in values
        ):
            raise ValueError(
                f"{field_name} must not contain empty values."
            )

    @classmethod
    def _validate_digest_tuple(
        cls,
        values: tuple[str, ...],
        field_name: str,
    ) -> None:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple."
            )

        for value in values:
            cls._validate_digest(value, field_name)

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