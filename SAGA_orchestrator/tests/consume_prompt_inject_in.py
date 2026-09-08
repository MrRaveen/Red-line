import os
import json
import threading
import logging
from flask import Flask, jsonify
from kafka import KafkaConsumer

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
PROMPT_INJECT_IN_TOPIC = os.getenv("PROMPT_INJECT_IN_TOPIC", "prompt_inject_in")
RESULTS_OUT_TOPIC = os.getenv("RESULTS_OUT_TOPIC", "results_out")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_TEST_GROUP", "test-saga-out-group")

def consume_topic(topic_name: str, group_suffix: str):
    """Background thread function to consume Kafka messages from a specific topic."""
    group_id = f"{KAFKA_CONSUMER_GROUP}_{group_suffix}"
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        logger.info(f"Subscribed to topic '{topic_name}' on {KAFKA_BOOTSTRAP_SERVERS} with group_id '{group_id}'")

        for message in consumer:
            logger.info(f"\n==================== [{topic_name}] ====================")
            logger.info(f"Topic: {message.topic} | Partition: {message.partition} | Offset: {message.offset}")
            logger.info(f"Message Value:\n{json.dumps(message.value, indent=2)}")
            logger.info(f"====================/{topic_name}====================\n")
            
    except Exception as e:
        logger.error(f"Error in Kafka consumer thread for topic '{topic_name}': {e}")

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "message": f"Listening for messages on Kafka topics in 2 threads: {PROMPT_INJECT_IN_TOPIC} and {RESULTS_OUT_TOPIC}"
    })

if __name__ == '__main__':
    # Thread 1: Consume prompt_inject_in
    t1 = threading.Thread(
        target=consume_topic,
        args=(PROMPT_INJECT_IN_TOPIC, "prompt_inject_in"),
        name="Thread-PromptInjectIn",
        daemon=True
    )

    # Thread 2: Consume results_out
    t2 = threading.Thread(
        target=consume_topic,
        args=(RESULTS_OUT_TOPIC, "results_out"),
        name="Thread-ResultsOut",
        daemon=True
    )

    t1.start()
    t2.start()

    logger.info("Started 2 consumer threads for Kafka topics.")

    # Start the Flask app
    app.run(host='0.0.0.0', port=4001, debug=False)

