from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PolicyVersionBinding:
    """Immutable observer-only binding between a policy version and subject."""

    binding_id: str
    policy_id: str
    policy_version: str
    policy_hash: str
    subject_id: str
    bound_at: datetime
    issuer_id: str
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(self.binding_id, "binding_id")
        self._require_non_empty(self.policy_id, "policy_id")
        self._require_non_empty(
            self.policy_version,
            "policy_version",
        )
        self._require_non_empty(self.policy_hash, "policy_hash")
        self._require_non_empty(self.subject_id, "subject_id")
        self._require_non_empty(self.issuer_id, "issuer_id")

        if not isinstance(self.bound_at, datetime):
            raise TypeError("bound_at must be a datetime.")

        if (
            self.bound_at.tzinfo is None
            or self.bound_at.utcoffset() is None
        ):
            raise ValueError(
                "bound_at must be timezone-aware."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "PolicyVersionBinding must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "PolicyVersionBinding must not permit side effects."
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