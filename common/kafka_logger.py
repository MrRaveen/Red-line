from .kafka_producer import send_message
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# Target topic for all logging (configurable if needed)
KAFKA_TOPIC = "raw_req_topic"

# ============================================================
# Pydantic Models
# ============================================================

class TransactionData(BaseModel):
    """Node transaction state data"""
    node_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None
    variation_count: Optional[int] = None
    inc_variation_count: Optional[int] = None
    breach_detected: Optional[bool] = None
    userID: str
    job_id: str

class ExecutionLogData(BaseModel):
    """Execution log entry"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_level: str = Field(..., pattern="^(INFO|WARNING|ERROR|DEBUG)$")
    message_type: str = Field(..., description="e.g., node_header, word_substitution, execute, etc.")
    message_text: str
    attack_prompt: Optional[str] = None
    target_response: Optional[str] = None
    status_code: Optional[str] = None
    verdict: Optional[str] = None
    evidence: Optional[str] = None
    userID: str
    job_id: str

# ============================================================
# Sending functions
# ============================================================

def send_transaction_data(payload: Dict[str, Any]) -> bool:
    """Validate payload as TransactionData and send to Kafka topic."""
    try:
        # Validate
        validated = TransactionData(**payload)
        # Convert to JSON (Pydantic v2: .model_dump())
        data = validated.model_dump(mode="json")
        # Send
        ok = send_message(KAFKA_TOPIC, data)
        if ok:
            logger.info(f"Transaction data sent to {KAFKA_TOPIC}: {data['node_name']}")
        else:
            logger.warning(f"Failed to send transaction data for {data['node_name']}")
        return ok
    except Exception as e:
        logger.error(f"Error sending transaction data: {e}")
        return False

def send_execution_log(payload: Dict[str, Any]) -> bool:
    """Validate payload as ExecutionLogData and send to Kafka topic."""
    try:
        # Validate
        validated = ExecutionLogData(**payload)
        # Convert to JSON
        data = validated.model_dump(mode="json")
        # Send
        ok = send_message(KAFKA_TOPIC, data)
        if ok:
            logger.info(f"Execution log sent to {KAFKA_TOPIC}: {data['message_type']}")
        else:
            logger.warning(f"Failed to send execution log for {data['message_type']}")
        return ok
    except Exception as e:
        logger.error(f"Error sending execution log: {e}")
        return False