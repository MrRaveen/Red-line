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
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
JUDGE_OUT_TOPIC = os.getenv("JUDGE_OUT_TOPIC", "judge_out_topic")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_TEST_GROUP", "test-judge-out-group")

def consume_judge_out_topic():
    """Background thread function to consume Kafka messages."""
    try:
        consumer = KafkaConsumer(
            JUDGE_OUT_TOPIC,
            bootstrap_servers="localhost:29092",
            group_id="test_judge_consumer",
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        logger.info(f"Subscribed to topic '{JUDGE_OUT_TOPIC}' on localhost:29092")

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
        "message": f"Listening for messages on Kafka topic: {JUDGE_OUT_TOPIC}"
    })

if __name__ == '__main__':
    # Start the Kafka consumer in a background thread
    consumer_thread = threading.Thread(target=consume_judge_out_topic, daemon=True)
    consumer_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=4000, debug=False)





