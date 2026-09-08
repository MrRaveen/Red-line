import os
import json
import logging
import requests
import time
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
SERVICE_RESULTS_OUT = os.getenv("SERVICE_RESULTS_OUT", "results_out")
SAGA_API_URL = os.getenv("SAGA_API_URL", "http://localhost:8001/api/v1/start-workflow")

# Sample testing payload for API
api_payload = {
    "userID": "test_user_001",
    "targetURL": "http://localhost:5000/api/generate",
    "job_name": "Test Prompt Injection Attack",
    "job_type": "prompt injection"
}

# Sample testing payload simulating a finished step in Kafka
kafka_payload = {
    "userID": "test_user_001",
    "job_id": "6a9f4b0d69b6da51775728ab", # Replace with actual job ID from API or logs
    "including_job_id": "6a9f4b0d69b6da51775728ab", # Replace with actual step ID from logs
    "status": "SUCCESS",
    "output_data": {
        "score": 0.95,
        "details": "Attack was successful."
    }
}

def trigger_api():
    try:
        logger.info(f"Triggering workflow via API at {SAGA_API_URL}...")
        response = requests.post(SAGA_API_URL, json=api_payload)
        logger.info(f"API Response [{response.status_code}]: {response.text}")
    except Exception as e:
        logger.error(f"Failed to trigger API: {e}")

def send_test_message():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        
        logger.info(f"Sending test payload to topic '{SERVICE_RESULTS_OUT}' on {KAFKA_BOOTSTRAP_SERVERS}...")
        future = producer.send(SERVICE_RESULTS_OUT, value=kafka_payload)
        record_metadata = future.get(timeout=10)
        
        logger.info(f"Successfully sent message to topic '{record_metadata.topic}' [Partition {record_metadata.partition}] @ offset {record_metadata.offset}")
        producer.flush()
        producer.close()
    except Exception as e:
        logger.error(f"Failed to send test message: {e}")

if __name__ == "__main__":
    logger.info("1. Triggering Workflow API...")
    # trigger_api()
    
    logger.info("2. Waiting a few seconds for the API to create the Job...")
    time.sleep(3)
    
    logger.info("3. Sending Kafka result message...")
    logger.info("IMPORTANT: Update 'job_id' and 'including_job_id' in this script with actual IDs from MongoDB or logs for the Kafka consumer to work properly!")
    send_test_message()
