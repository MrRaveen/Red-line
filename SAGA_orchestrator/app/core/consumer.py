import json
import signal
import logging
import os
import sys
from kafka import KafkaConsumer
from bson.objectid import ObjectId

# Ensure common is accessible for Kafka producer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common.kafka_producer import send_message

from app.core.models.job import (
    update_including_job,
    get_job,
    update_job_status,
    create_including_job,
    including_jobs_collection,
    JobStatus
)
from app.core.nextStepChecker import get_next_step
from app.core.formats.promot_injection_v1_format import get_format_model

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
    RESULTS_OUT = os.getenv("RESULTS_OUT","results_out")

    consumer = KafkaConsumer(
        RESULTS_OUT,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="saga_orchestrator_consumer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False  # Disabled to prevent data loss on crash
    )
    
    logger.info(f"Consumer started on topic '{RESULTS_OUT}'")
    
    try:
        while running:
            # Poll with timeout to allow checking the 'running' flag
            records = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in records.items():
                for msg in messages:
                    try:
                        data = json.loads(msg.value) if isinstance(msg.value, str) else msg.value
                        
                        state_after = data.get("state_after", {})
                        job_id = state_after.get("job_ID") or data.get("job_id")
                        including_job_id = state_after.get("including_job_id") or data.get("including_job_id")
                        user_id = state_after.get("userID") or data.get("userID")
                        
                        if not job_id or not including_job_id:
                            logger.error(f"Event missing job_id or including_job_id: {data}")
                            continue
                            
                        logger.info(f"Received results for job {job_id}, step id {including_job_id}")

                        # 1. Get the current step details from DB to know its name
                        current_step_record = including_jobs_collection.find_one({"_id": ObjectId(including_job_id)})
                        if not current_step_record:
                            logger.error(f"Could not find including_job with ID {including_job_id}")
                            continue
                            
                        current_step_name = current_step_record.get("jobName")

                        # 2. Update the completed including_job status
                        status_str = data.get("status", "FINISHED")
                        step_status = JobStatus.FINISHED if status_str.upper() == "SUCCESS" or status_str.upper() == "FINISHED" else JobStatus.PROCESSING
                        # Assuming any non-success string could mean FAILED or PROGRESS, but typically it finishes here
                        
                        update_including_job(including_job_id, output_data=data, status=JobStatus.FINISHED)
                        
                        # 3. Get the parent job to find the workflow ID
                        parent_job = get_job(job_id)
                        if not parent_job:
                            logger.error(f"Parent job {job_id} not found in database.")
                            continue
                            
                        workflow_id = parent_job.get("workflowID")
                        
                        # 4. Determine the next step
                        next_step = get_next_step(workflow_id, current_step_name)
                        
                        if next_step:
                            logger.info(f"Advancing job {job_id} to next step: {next_step['name']}")
                            
                            # 5. Create new including_job for the next step
                            new_including_job_id = create_including_job(job_id, next_step["name"], input_data=data)
                            
                            # 6. Format the payload if a format is specified
                            payload_data = data.copy()
                            payload_data["including_job_id"] = new_including_job_id
                            
                            format_name = next_step.get("format")
                            topic_in = next_step.get("topicIn")
                            
                            if format_name:
                                FormatModelClass = get_format_model(format_name)
                                if FormatModelClass:
                                    # We try to validate against the model, missing fields will raise exception
                                    payload_data = FormatModelClass(**payload_data).model_dump(mode='json')
                                else:
                                    logger.warning(f"Format model {format_name} not found in registry. Sending raw payload.")
                                    
                            if topic_in:
                                send_message(topic_in, payload_data)
                                logger.info(f"Successfully published next step to {topic_in}")
                            else:
                                logger.error(f"Next step {next_step['name']} has no 'topicIn' defined.")
                        else:
                            logger.info(f"No more steps for workflow {workflow_id}. Marking job {job_id} as FINISHED.")
                            update_job_status(job_id, JobStatus.FINISHED)
                        
                    except Exception as e:
                        logger.error(f"Error handling message at offset {msg.offset}: {e}", exc_info=True)
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
    start_consumer()
