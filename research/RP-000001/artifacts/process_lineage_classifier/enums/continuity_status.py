from enum import Enum


class ContinuityStatus(str, Enum):
    """Continuity outcomes for prototype version 0.1."""

    CONTINUOUS = "CONTINUOUS"
    CONDITIONALLY_CONTINUOUS = "CONDITIONALLY_CONTINUOUS"
    DEGRADED = "DEGRADED"
    INTERRUPTED = "INTERRUPTED"
    TERMINATED = "TERMINATED"
    UNVERIFIED = "UNVERIFIED"
    UNKNOWN = "UNKNOWN"