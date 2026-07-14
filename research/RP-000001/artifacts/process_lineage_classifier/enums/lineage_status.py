from enum import Enum


class LineageStatus(str, Enum):
    """Lineage structures for prototype version 0.1."""

    LINEAR = "LINEAR"
    RESTORED = "RESTORED"
    SHARED_PARENT = "SHARED_PARENT"
    BRANCHED = "BRANCHED"
    MERGED = "MERGED"
    NEW_ROOT = "NEW_ROOT"
    DISCONTINUOUS = "DISCONTINUOUS"
    UNVERIFIED = "UNVERIFIED"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"
    RECONCILED = "RECONCILED"