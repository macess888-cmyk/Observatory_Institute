from enum import Enum


class EventType(str, Enum):
    """Supported process-lineage event types for prototype version 0.1."""

    START = "START"
    ADDRESS_CHANGE = "ADDRESS_CHANGE"
    RESTART = "RESTART"
    MIGRATE = "MIGRATE"
    RESTORE = "RESTORE"
    CLONE = "CLONE"
    BRANCH = "BRANCH"
    MERGE = "MERGE"
    UNKNOWN_EVENT = "UNKNOWN_EVENT"