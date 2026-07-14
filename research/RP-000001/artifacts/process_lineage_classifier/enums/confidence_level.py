from enum import Enum


class ConfidenceLevel(str, Enum):
    """Evidence-completeness confidence levels for prototype version 0.1."""

    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"