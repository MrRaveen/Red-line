import os
import sys
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# Ensure repository root is in sys.path so 'common' package can be imported
_curr = os.path.abspath(os.path.dirname(__file__))
while _curr and _curr != os.path.dirname(_curr):
    if os.path.exists(os.path.join(_curr, "common")):
        if _curr not in sys.path:
            sys.path.insert(0, _curr)
        break
    _curr = os.path.dirname(_curr)

from common.enums.JobTypeEnum import JobType

class JudgeFormatV1(BaseModel):
    node_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    job_type: JobType
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None
    extra_observations: Optional[Dict[str, Any]] = None
    userID: str
    job_id: str

