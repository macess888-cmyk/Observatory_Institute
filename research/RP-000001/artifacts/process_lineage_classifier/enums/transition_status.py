from enum import Enum


class TransitionStatus(str, Enum):
    """Transition outcomes for prototype version 0.1."""

    STARTED = "STARTED"
    ADDRESS_REBOUND = "ADDRESS_REBOUND"
    RESTARTED = "RESTARTED"
    MIGRATED = "MIGRATED"
    RESTORED = "RESTORED"
    CLONED = "CLONED"
    BRANCHED = "BRANCHED"
    MERGED = "MERGED"
    REPLACED = "REPLACED"
    NEW_ROOT = "NEW_ROOT"
    UNKNOWN = "UNKNOWN"