import json
import signal
import logging
import os
import sys
from datetime import datetime
from kafka import KafkaConsumer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.config import Config
from common.kafka_producer import send_message

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

def start_consumer():
    KAFKA_BOOTSTRAP_SERVERS = Config.KAFKA_BOOTSTRAP_SERVERS
    PREPROCESSOR_IN_TOPIC = Config.PREPROCESSOR_IN_TOPIC
    KAFKA_TOPIC_SEND_PREPROCESSED = Config.KAFKA_TOPIC_SEND_PREPROCESSED

    consumer = KafkaConsumer(
        PREPROCESSOR_IN_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="preprocessor_consumer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )
    
    logger.info(f"Consumer started on topic '{PREPROCESSOR_IN_TOPIC}' -> '{KAFKA_TOPIC_SEND_PREPROCESSED}'")
    
    try:
        while running:
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
                        
                        # Preprocessing logic matching the streams setup
                        data.setdefault("processed_at", datetime.utcnow().isoformat())
                        logger.info(f"Preprocessing payload: {data}")
                        
                        # Send to the preprocessed topic using common producer
                        ok = send_message(KAFKA_TOPIC_SEND_PREPROCESSED, data)
                        if not ok:
                            logger.error(f"Failed to send preprocessed message for offset {msg.offset}")
                        
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
