from app import db
from datetime import datetime
from common.enums.LogLevelEnum import LogLevel
from common.enums.MessageTypeEnum import MessageType

class JobLogs(db.Document):
    meta = {
        "collection": "job_logs",
        "indexes": [
            "userID",
            "job_id",
            "log_level",
            "message_type",
            "timestamp",
            ("job_id", "timestamp"),          # primary access pattern: logs for a job in order
            ("userID", "timestamp"),          # user-level activity feed
        ],
        "ordering": ["timestamp"],            # chronological by default
    }

    # ---- Timing ----------------------------------------------------------
    timestamp = db.DateTimeField(default=datetime.utcnow, required=True)

    # ---- Classification --------------------------------------------------
    log_level    = db.StringField(required=True, choices=[e.value for e in LogLevel], default=LogLevel.INFO.value)
    message_type = db.StringField(required=True, choices=[e.value for e in MessageType])

    # ---- Payload ---------------------------------------------------------
    message_text        = db.StringField(required=True, max_length=5000)
    attack_prompt       = db.StringField()
    target_response     = db.StringField()
    status_code         = db.IntField()
    verdict             = db.StringField(max_length=64)
    evidence            = db.DictField()
    extra_observations  = db.DictField()

    # ---- Ownership / linkage --------------------------------------------
    userID = db.StringField(required=True, max_length=128)
    job_id = db.StringField(required=True, max_length=64)
