from app.graphs.main_graph.kafka_logger import ExecutionLogData
from app.graphs.main_graph.kafka_logger import TransactionData
from app.graphs.main_graph.kafka_beta.config import Config
import json
import logging
import threading

from flask import Flask, jsonify
from kafka import KafkaConsumer
from pymongo import MongoClient
from pydantic import ValidationError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DB]
transactions_col = db[Config.MONGO_COLLECTION_TRANSACTIONS]
execution_col = db[Config.MONGO_COLLECTION_EXECUTION]

app = Flask(__name__)

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
            # Validate using TransactionData model (but it doesn't have state_before? Actually it does)
            # TransactionData expects node_name, state_before, state_after etc.
            validated = TransactionData(**msg_value)
            doc = validated.model_dump(mode="json")
            save_document(transactions_col, doc)
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
    """Background Kafka consumer thread."""
    consumer = KafkaConsumer(
        Config.KAFKA_TOPIC_SEND_PREPROCESSED,
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        group_id='log_processor',
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    logger.info(f"Log processor consumer started on topic '{Config.KAFKA_TOPIC_SEND_PREPROCESSED}'")
    for msg in consumer:
        try:
            msg_type = process_message(msg.value)
            logger.info(f"Processed message of type: {msg_type}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

def run_consumer_in_background():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
    return thread

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "log-processor",
        "kafka_topic": Config.KAFKA_TOPIC_PREPROCESSED,
        "mongo_db": Config.MONGO_DB
    })

if __name__ == "__main__":
    run_consumer_in_background()
    app.run(host="0.0.0.0", port=Config.FLASK_PORT_LOG_PROCESSOR, debug=False)