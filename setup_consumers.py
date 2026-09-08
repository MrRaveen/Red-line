import os

requirements_content = """Flask
gunicorn
semantic-kernel
openai
pydantic-settings
python-dotenv
langgraph
langchain-core     
langgraph-checkpoint-postgres   
requests
sqlalchemy
sentence_transformers
kafka-python
pydantic
redis"""

dockerfile_template = """FROM python:3.11-slim

WORKDIR /app

COPY {folder}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY {folder}/app/ ./app/
COPY {folder}/wsgi.py .
COPY {folder}/run.py .
COPY common/ ./common/

CMD ["gunicorn", "--bind", "0.0.0.0:{port}", "wsgi:app"]"""

consumer_template = """import json
import signal
import logging
import os
import sys
from kafka import KafkaConsumer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

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
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    {topic_var} = os.getenv("{topic_var}", "{topic_val}")

    consumer = KafkaConsumer(
        {topic_var},
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="{group_id}",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )
    
    logger.info(f"Consumer started on topic '{{{topic_var}}}'")
    
    try:
        while running:
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
                        logger.info(f"Received request: {{data}}")
                        
                    except Exception as e:
                        logger.error(f"Error handling message at offset {{msg.offset}}: {{e}}", exc_info=True)
                
            if records:
                consumer.commit()
                
    except Exception as e:
        logger.critical(f"Fatal consumer error: {{e}}")
    finally:
        logger.info("Closing Kafka connection and leaving consumer group...")
        consumer.close()

if __name__ == "__main__":
    start_consumer()"""

services = [
    {"folder": "jailbreak_attack", "port": 8003, "topic_var": "JAILBREAK_REQ_TOPIC", "topic_val": "jailbreak_req_topic", "group_id": "jailbreak_attack_consumer"},
    {"folder": "hallucination_attack", "port": 8004, "topic_var": "HALLUCINATION_REQ_TOPIC", "topic_val": "hallucination_req_topic", "group_id": "hallucination_attack_consumer"},
    {"folder": "prompt_injection_attack_new", "port": 8005, "topic_var": "PROMPT_REQ_TOPIC", "topic_val": "prompt_req_topic", "group_id": "prompt_injection_consumer"}
]

for svc in services:
    folder = svc["folder"]
    os.makedirs(f"{folder}/app/consumer", exist_ok=True)
    
    with open(f"{folder}/requirements.txt", "w") as f:
        f.write(requirements_content)
        
    with open(f"{folder}/Dockerfile", "w") as f:
        f.write(dockerfile_template.format(folder=folder, port=svc["port"]))
        
    with open(f"{folder}/app/consumer/v1_consumer.py", "w") as f:
        f.write(consumer_template.format(topic_var=svc["topic_var"], topic_val=svc["topic_val"], group_id=svc["group_id"]))
        
print("Success")
