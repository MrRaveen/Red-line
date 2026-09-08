from ..config import Config
import asyncio
from app.services.execute import JudgeAgentExecution
import json
import signal
import logging
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for OS signal handling
running = True

def graceful_shutdown(sig, frame):
    global running
    logger.info("Shutdown signal received. Terminating judge consumer safely...")
    running = False

# Bind Docker/Kubernetes termination signals
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def start_consumer_for_judge_agent():
    consumer = KafkaConsumer(
        Config.JUDGE_IN_TOPIC,
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        group_id="judge_consumer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False  # Disabled to prevent data loss on crash
    )
    
    logger.info(f"Consumer started on topic '{Config.JUDGE_IN_TOPIC}'")
    
    try:
        while running:
            # Poll with timeout to allow checking the 'running' flag
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
            
                        # Extract fields with defaults
                        userID = data.get("userID")
                        job_id = data.get("job_id")
                        target_url = data.get("target_url")
                        budget = data.get("budget")
                        total_breaches = data.get("total_breaches")
                        attempts = data.get("attempts")  # could be list or None

                        # Create and run the agent asynchronously
                        jae = JudgeAgentExecution()
                        result = asyncio.run(jae.run(
                            userID=userID,
                            job_id=job_id,
                            target_url=target_url,
                            budget=budget,
                            total_breaches=total_breaches,
                            attempts=attempts
                        ))
                        
                        # Handle result (e.g., log success, store to DB)
                        logger.info(f"Judge execution completed with result: {result}")
                        
                    except Exception as e:
                        logger.error(f"Error handling message at offset {msg.offset}: {e}")
                        # Insert DLQ routing logic here for failed messages
                
            # Commit offsets only after the batch has successfully processed
            if records:
                consumer.commit()
                
    except Exception as e:
        logger.critical(f"Fatal consumer error: {e}")
    finally:
        logger.info("Closing Kafka connection and leaving consumer group...")
        consumer.close()

if __name__ == "__main__":
    start_consumer_for_judge_agent()