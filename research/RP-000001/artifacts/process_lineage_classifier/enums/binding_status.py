from enum import Enum


class BindingStatus(str, Enum):
    """Binding-integrity outcomes for prototype version 0.1."""

    BOUND = "BOUND"
    CONDITIONALLY_BOUND = "CONDITIONALLY_BOUND"
    REBOUND = "REBOUND"
    COLLIDING = "COLLIDING"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"