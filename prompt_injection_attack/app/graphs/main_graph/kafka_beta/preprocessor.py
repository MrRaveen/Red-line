# app/graphs/main_graph/kafka_beta/preprocessor.py
import json
import logging
from datetime import datetime
from typing import Any, Dict

from app.graphs.main_graph.kafka_beta.config import Config
from app.graphs.main_graph.kafka_beta.producer import send_message

logger = logging.getLogger(__name__)

def kafka_streams(msg):
    """
    Preprocess an incoming Kafka message:
    1. Extract the JSON value.
    2. Validate/clean it (optional).
    3. Add processing metadata.
    4. Forward to the output topic.
    """
    try:
        # Extract the actual payload (already JSON-decoded by the consumer's deserializer)
        payload = msg.value
        
        # If payload is a dict, assume it's already structured; else try to parse
        if isinstance(payload, dict):
            data = payload
        else:
            data = json.loads(payload)
        
        # Add a processed timestamp (if not present)
        data.setdefault("processed_at", datetime.utcnow().isoformat())
        
        # Optionally, filter or transform fields here
        # For example, extract message_type or node_name for routing
        # message_type = data.get("message_type") or data.get("node_name")
        
        # Log for debugging
        logger.info(f"Preprocessing payload: {data}")
        
        # Send to the preprocessed topic
        ok = send_message(Config.KAFKA_TOPIC_SEND_PREPROCESSED, data)
        if not ok:
            logger.error("Failed to send preprocessed message")
        return ok
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        return False