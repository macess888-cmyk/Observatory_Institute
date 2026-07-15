from enum import Enum


class WitnessTrustLevel(str, Enum):
    """Trust levels assigned to witness sources."""

    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNTRUSTED = "UNTRUSTED"