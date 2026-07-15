from enum import Enum


class RecoveryDecisionStatus(str, Enum):
    """Observer-only recovery orchestration outcomes."""

    RECOVERY_READY = "RECOVERY_READY"
    RECOVERY_HOLD = "RECOVERY_HOLD"