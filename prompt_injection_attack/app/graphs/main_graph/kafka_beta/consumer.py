from app.graphs.main_graph.kafka_beta.preprocessor import kafka_streams
import json
import threading
import logging
from kafka import KafkaConsumer
from app.graphs.main_graph.kafka_beta.config import Config
from flask import Flask
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_consumer(topic, group_id, bootstrap_servers):
    """
    Runs in a background thread. Reads messages forever and calls
    on_message(message_dict) for each one.
    """
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    logger.info(f"Consumer started on topic '{topic}'")
    for msg in consumer:
        try:
            logger.info(f"Test consumer received from {topic}: {msg.value}")
            kafka_streams(msg)
        except Exception as e:
            logger.error(f"Error handling message: {e}")


def run_consumer_in_background(topic, group_id, bootstrap_servers):
    """Starts the consumer loop on a separate thread so Flask isn't blocked."""
    thread = threading.Thread(
        target=start_consumer,
        args=(topic, group_id, bootstrap_servers),
        daemon=True,
    )
    thread.start()
    return thread

def start_test_consumer(topic, group_id, bootstrap_servers):
    """
    Runs in a background thread for testing. Reads messages from the preprocessed topic.
    """
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    logger.info(f"Test consumer started on topic '{topic}'")
    for msg in consumer:
        try:
            logger.info(f"Test consumer received from {topic}: {msg.value}")
        except Exception as e:
            logger.error(f"Error in test consumer: {e}")

def run_test_consumer_in_background(topic, group_id, bootstrap_servers):
    thread = threading.Thread(
        target=start_test_consumer,
        args=(topic, group_id, bootstrap_servers),
        daemon=True,
    )
    thread.start()
    return thread

app = Flask(__name__)

if __name__ == "__main__":
    run_consumer_in_background(
        topic=Config.KAFKA_TOPIC_GET_PREPROCESSED,
        group_id=Config.KAFKA_CONSUMER_GROUP,
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS
    )
    run_test_consumer_in_background(
        topic=Config.KAFKA_TOPIC_SEND_PREPROCESSED,
        group_id=Config.KAFKA_CONSUMER_GROUP,
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS
    )
    app.run(host="0.0.0.0", port=Config.FLASK_PORT_KAFKA_SERVICE, debug=False)
   
