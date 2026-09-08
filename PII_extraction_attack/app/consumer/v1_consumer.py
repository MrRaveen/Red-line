import json
import signal
import logging
import os
import sys
from kafka import KafkaConsumer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from app.services.graph_service import execute_pii_graph_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.config import Config
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
    PII_INJECT_IN_TOPIC = Config.PII_INJECT_IN_TOPIC

    consumer = KafkaConsumer(
        PII_INJECT_IN_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="pii_extraction_consumer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )
    
    logger.info(f"Consumer started on topic '{PII_INJECT_IN_TOPIC}'")
    
    try:
        while running:
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
                        logger.info(f"Received PII extraction request: {data}")
                        # Logic will be implemented later
                        
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
