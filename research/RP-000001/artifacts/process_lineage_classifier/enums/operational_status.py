from enum import Enum


class OperationalStatus(str, Enum):
    """Operational outcomes for prototype version 0.1."""

    PASS = "PASS"
    HOLD = "HOLD"
    FAIL = "FAIL"