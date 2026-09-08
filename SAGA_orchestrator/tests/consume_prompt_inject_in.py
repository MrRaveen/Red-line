import os
import json
import threading
import logging
from flask import Flask, jsonify
from kafka import KafkaConsumer

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
PROMPT_INJECT_IN_TOPIC = os.getenv("PROMPT_INJECT_IN_TOPIC", "prompt_inject_in")
RESULTS_OUT = os.getenv("RESULTS_OUT", "results_out")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_TEST_GROUP", "test-saga-out-group")

def consume_topics():
    """Background thread function to consume Kafka messages."""
    try:
        consumer = KafkaConsumer(
            PROMPT_INJECT_IN_TOPIC,
            RESULTS_OUT,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        logger.info(f"Subscribed to topics '{PROMPT_INJECT_IN_TOPIC}' and '{RESULTS_OUT}' on {KAFKA_BOOTSTRAP_SERVERS}")

        for message in consumer:
            logger.info("==================================================")
            logger.info(f"Received message on topic: {message.topic}")
            logger.info(f"Message Value: {json.dumps(message.value, indent=2)}")
            logger.info("==================================================")
            
    except Exception as e:
        logger.error(f"Error in Kafka consumer thread: {e}")

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "message": f"Listening for messages on Kafka topics: {PROMPT_INJECT_IN_TOPIC} and {RESULTS_OUT}"
    })

if __name__ == '__main__':
    # Start the Kafka consumer in a background thread
    consumer_thread = threading.Thread(target=consume_topics, daemon=True)
    consumer_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=4001, debug=False)
