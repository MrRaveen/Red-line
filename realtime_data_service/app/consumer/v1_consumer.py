from app.config import Config
import json
import signal
import logging
import os
import sys
from kafka import KafkaConsumer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    RESULTS_OUT = Config.RESULTS_OUT

    consumer = KafkaConsumer(
        RESULTS_OUT,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="results_out_consume",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )
    
    logger.info(f"Consumer started on topic '{RESULTS_OUT}'")
    
    try:
        while running:
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
                        logger.info(f"realtime service : {data}")
                        Config.r.publish(Config.REDIS_PUBSUB_PART,json.dumps(data))
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
