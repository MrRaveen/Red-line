import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka.config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_producer():
    """Create a Kafka producer. Reused across requests."""
    return KafkaProducer(
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
        acks="all",  # wait for all replicas to confirm the write
    )


def send_message(topic, message: dict):
    """Send one message and wait for confirmation (or raise error)."""
    try:
        producer = get_producer()
        future = producer.send(topic, value=message)
        result = future.get(timeout=10)  # blocks until sent or times out
        logger.info(f"Sent message to {result.topic} partition {result.partition}")
        return True
    except KafkaError as e:
        logger.error(f"Failed to send message: {e}")
        return False