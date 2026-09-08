from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class JudgeFormatV1(BaseModel):
    userID: str
    job_id: str
    including_job_id: str
    target_url: Optional[str] = None
    budget: Optional[int] = None
    total_breaches: Optional[int] = 0
    attempts: Optional[List[Any]] = []
    extra_observations: Optional[Dict[str, Any]] = {}
