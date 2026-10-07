from enum import Enum
class JobStatus(str, Enum):
    """Allowed job lifecycle states."""
    PENDING   = "PENDING"
    RUNNING   = "RUNNING"
    FINISHED  = "FINISHED"
    FAILED    = "FAILED"
    CANCELLED = "CANCELLED"

    