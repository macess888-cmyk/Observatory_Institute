from datetime import datetime

from models import PolicyVersionBinding, QuorumPolicy


class PolicyVersionBindingError(ValueError):
    """Raised when a policy-version binding is invalid."""


class PolicyVersionBindingValidator:
    """Validates a policy-version binding against an expected policy."""

    def validate(
        self,
        binding: PolicyVersionBinding,
        policy: QuorumPolicy,
        *,
        expected_policy_version: str,
        expected_policy_hash: str,
        subject_id: str,
        now: datetime,
    ) -> bool:
        if not isinstance(binding, PolicyVersionBinding):
            raise TypeError(
                "binding must be a PolicyVersionBinding."
            )

        if not isinstance(policy, QuorumPolicy):
            raise TypeError(
                "policy must be a QuorumPolicy."
            )

        self._require_non_empty(
            expected_policy_version,
            "expected_policy_version",
        )
        self._require_non_empty(
            expected_policy_hash,
            "expected_policy_hash",
        )
        self._require_non_empty(subject_id, "subject_id")
        self._require_timezone_aware(now)

        if binding.policy_id != policy.policy_id:
            raise PolicyVersionBindingError(
                "Policy binding contains a policy identity mismatch."
            )

        if binding.policy_version != expected_policy_version:
            raise PolicyVersionBindingError(
                "Policy binding contains a policy version mismatch."
            )

        if binding.policy_hash != expected_policy_hash:
            raise PolicyVersionBindingError(
                "Policy binding contains a policy hash mismatch."
            )

        if binding.subject_id != subject_id:
            raise PolicyVersionBindingError(
                "Policy binding contains a subject mismatch."
            )

        if binding.bound_at > now:
            raise PolicyVersionBindingError(
                "Policy binding timestamp is in the future."
            )

        return True

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

    @staticmethod
    def _require_timezone_aware(
        value: datetime,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(
                "now must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise TypeError(
                "now must be timezone-aware."
            )