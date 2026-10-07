from app import db, jwt
from datetime import datetime
from common.enums.JobStatusEnum import JobStatus
from common.enums.JobTypeEnum import JobType
class Jobs(db.Document):
    meta = {
        "collection": "jobs",
        "indexes": [
            "userID",
            "job_status",
            "job_type",
            "workflowID",
            "created_date",
            ("userID", "created_date"),
            ("userID", "job_status"),
        ],
        "ordering": ["-created_date"],
    }

    userID = db.StringField(required=True, max_length=128)
    targetURL = db.URLField(required=True)

    # ---- Job metadata ---------------------------------------------------
    job_name    = db.StringField(required=True, max_length=200)
    description = db.StringField(max_length=2000)
    job_type    = db.StringField(required=True, choices=[e.value for e in JobType])
    workflowID  = db.StringField(required=True, max_length=128)

    # ---- Lifecycle ------------------------------------------------------
    created_date = db.DateTimeField(default=datetime.utcnow, required=True)
    updated_date = db.DateTimeField(default=datetime.utcnow)
    job_status   = db.StringField(
        required=True,
        choices=[e.value for e in JobStatus],
        default=JobStatus.PENDING.value,
    )

    # ---- Result counters ------------------------------------------------
    breachedCount           = db.IntField(default=0, min_value=0)
    totalExecutedCategories = db.IntField(default=0, min_value=0)
    nonBreachedCategories   = db.IntField(default=0, min_value=0)
