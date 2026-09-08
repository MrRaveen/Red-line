from common.kafka_producer import send_message
import json
import signal
import logging
import os
import sys
from kafka import KafkaConsumer
from pymongo import MongoClient
from pydantic import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.config import Config
from common.kafka_logger import TransactionData, ExecutionLogData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for OS signal handling
running = True

def graceful_shutdown(sig, frame):
    global running
    logger.info("Shutdown signal received. Terminating consumer safely...")
    running = False

# Bind Docker/Kubernetes termination signals
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

# MongoDB client
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DB]
transactions_col = db[Config.MONGO_COLLECTION_TRANSACTIONS]
execution_col = db[Config.MONGO_COLLECTION_EXECUTION]

def save_document(collection, doc):
    """Insert a document and return its ObjectId."""
    result = collection.insert_one(doc)
    logger.info(f"Inserted document with _id: {result.inserted_id}")
    return result.inserted_id

def process_message(msg_value):
    """
    Determine message type (transaction vs execution log) and store in MongoDB.
    msg_value is a dict already deserialized by KafkaConsumer.
    """
    # Validate and classify
    if "node_name" in msg_value and "state_before" in msg_value:
        # Transaction data
        try:
            validated = TransactionData(**msg_value)
            doc = validated.model_dump(mode="json")
            save_document(transactions_col, doc)
            nodeName = validated.node_name
            if nodeName == Config.NODE_COMPLETE:
                send_message(Config.RESULTS_OUT,doc)
            return "transaction"
        except ValidationError as e:
            logger.error(f"Invalid transaction data: {e}")
    elif "message_type" in msg_value and "message_text" in msg_value:
        # Execution log
        try:
            validated = ExecutionLogData(**msg_value)
            doc = validated.model_dump(mode="json")
            save_document(execution_col, doc)
            return "execution"
        except ValidationError as e:
            logger.error(f"Invalid execution log: {e}")
    else:
        logger.warning(f"Unknown message type: {msg_value}")

    return None

def start_consumer():
    consumer = KafkaConsumer(
        Config.KAFKA_TOPIC_SEND_PREPROCESSED,
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        group_id='log_processor_consumer',
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )
    logger.info(f"Log processor consumer started on topic '{Config.KAFKA_TOPIC_SEND_PREPROCESSED}'")
    
    try:
        while running:
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
                        msg_type = process_message(data)
                        if msg_type:
                            logger.info(f"Processed message of type: {msg_type}")
                    except Exception as e:
                        logger.error(f"Error handling message at offset {msg.offset}: {e}", exc_info=True)
                        
            if records:
                consumer.commit()
    except Exception as e:
        logger.critical(f"Fatal consumer error: {e}")
    finally:
        logger.info("Closing Kafka connection and leaving consumer group...")
        consumer.close()

if __name__ == "__main__":
    start_consumer()
