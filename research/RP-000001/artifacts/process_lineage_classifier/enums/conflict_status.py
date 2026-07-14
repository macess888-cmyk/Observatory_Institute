from enum import Enum


class ConflictStatus(str, Enum):
    """Conflict outcomes for prototype version 0.1."""

    CLEAR = "CLEAR"
    CONFLICTED = "CONFLICTED"
    COLLIDING = "COLLIDING"
    UNKNOWN = "UNKNOWN"