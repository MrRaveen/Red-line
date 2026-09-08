import os
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from pymongo import MongoClient
from typing import Any
from app.config import Config

# MongoDB setup
MONGO_URI = Config.MONGO_URI
MONGO_DB = "redline_logs"
MONGO_COLLECTION_JOBS = "jobs"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
jobs_collection = db[MONGO_COLLECTION_JOBS]

class JobStatus(str, Enum):
    PROCESSING = "PROCESSING"
    FINISHED = "FINISHED"

class JobType(str, Enum):
    PROMPT_INJECTION = "prompt injection"
    HALLUCINATION_ATTACK = "halusination attack"
    PII_EXFILTRATION_ATTACK = "PII exfilteration attack"
    JAILBREAK_ATTACK = "jailbreak attack"
    ALL = "all"

class JobModel(BaseModel):
    userID: str
    targetURL: str
    job_name: str
    description: Optional[str] = ""
    job_type: JobType
    workflowID: Union[str, List[str]]
    created_date: datetime = Field(default_factory=datetime.utcnow)
    job_status: JobStatus = JobStatus.PROCESSING
    breachedCount: int = 0
    totalExecutedCategories: int = 0
    nonBreachedCategories: int = 0

def create_job(job_data: dict) -> str:
    """
    Validates the job data, inserts it into MongoDB, and returns the stringified job ID.
    """
    job = JobModel(**job_data)
    job_dict = job.model_dump(mode='json') # Convert datetime and enums to json-serializable
    
    result = jobs_collection.insert_one(job_dict)
    return str(result.inserted_id)

class IncludingJobModel(BaseModel):
    jobID: str
    status: JobStatus = JobStatus.PROCESSING
    jobName: str
    output: Any = None
    input: Any = None
    timestamp_created: datetime = Field(default_factory=datetime.utcnow)
    timestamp_updated: datetime = Field(default_factory=datetime.utcnow)

including_jobs_collection = db["including_jobs"]

def create_including_job(job_id: str, step_name: str, input_data: Any) -> str:
    """Creates a new step tracking record in MongoDB."""
    including_job = IncludingJobModel(
        jobID=job_id,
        jobName=step_name,
        input=input_data,
        status=JobStatus.PROCESSING
    )
    result = including_jobs_collection.insert_one(including_job.model_dump(mode='json'))
    return str(result.inserted_id)

from bson.objectid import ObjectId

def update_including_job(including_job_id: str, output_data: Any, status: JobStatus):
    """Updates an existing step tracking record."""
    including_jobs_collection.update_one(
        {"_id": ObjectId(including_job_id)},
        {"$set": {
            "output": output_data,
            "status": status.value if isinstance(status, JobStatus) else status,
            "timestamp_updated": datetime.utcnow().isoformat()
        }}
    )

def get_job(job_id: str) -> dict:
    """Fetches a parent Job document."""
    return jobs_collection.find_one({"_id": ObjectId(job_id)})

def update_job_status(job_id: str, status: JobStatus):
    """Updates parent Job status."""
    jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"job_status": status.value if isinstance(status, JobStatus) else status}}
    )
