import json
import os
import logging
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.core.models.job import create_job, JobType, create_including_job
from app.core.formats.promot_injection_v1_format import get_format_model
import sys

# Ensure common is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from common.kafka_producer import send_message

logger = logging.getLogger(__name__)

# Mapping job types to workflow IDs (JSON filenames)
WORKFLOW_MAP = {
    JobType.PROMPT_INJECTION: "prompt_injection_v1",
    JobType.HALLUCINATION_ATTACK: "hallucination_v1", # Placeholders for future
    JobType.PII_EXFILTRATION_ATTACK: "pii_v1",
    JobType.JAILBREAK_ATTACK: "jailbreak_v1",
}

@celery_app.task(name="start_workflow")
def start_workflow(job_payload: Dict[str, Any]):
    """
    Celery background task to start a workflow.
    Expects job_payload with user inputs.
    """
    logger.info(f"Starting workflow for payload: {job_payload}")
    
    try:
        job_type = JobType(job_payload.get("job_type"))
        
        # 1. Map job type to workflowID if not provided
        workflow_id = job_payload.get("workflowID")
        if not workflow_id:
            workflow_id = WORKFLOW_MAP.get(job_type)
            job_payload["workflowID"] = workflow_id
            
        if not workflow_id:
            raise ValueError(f"No workflow mapping found for job type: {job_type}")

        # 2. Save job to MongoDB and get job ID
        job_id = create_job(job_payload)
        logger.info(f"Created job with ID: {job_id}")

        # 3. Load workflow JSON
        workflow_path = os.path.join(os.path.dirname(__file__), f"../workflows/{workflow_id}.JSON")
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
            
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)

        steps = workflow_data.get("steps", [])
        if not steps:
            raise ValueError(f"No steps defined in workflow: {workflow_id}")

        first_step = steps[0]
        format_name = first_step.get("format")
        topic_in = first_step.get("topicIn")
        step_name = first_step.get("name")

        if not format_name or not topic_in or not step_name:
            raise ValueError("First step is missing 'format', 'topicIn', or 'name'")

        # 4. Prepare input JSON using the Pydantic model
        FormatModelClass = get_format_model(format_name)
        if not FormatModelClass:
            raise ValueError(f"Format model not found in registry: {format_name}")
            
        # Create including job to track this step
        including_job_id = create_including_job(job_id, step_name, job_payload)
        logger.info(f"Created including_job with ID: {including_job_id} for step: {step_name}")

        # Map input parameters to the pydantic model
        payload_data = {
            "userID": job_payload.get("userID"),
            "job_id": job_id,
            "including_job_id": including_job_id,
            "targetURL": job_payload.get("targetURL")
        }

        # Validate and serialize payload
        validated_payload = FormatModelClass(**payload_data).model_dump(mode='json')
        
        # 5. Produce to Kafka topic
        success = send_message(topic_in, validated_payload)
        if success:
            logger.info(f"Successfully produced message to topic '{topic_in}' for job {job_id}")
        else:
            logger.error(f"Failed to produce message to topic '{topic_in}' for job {job_id}")
            
        return {"job_id": job_id, "status": "success", "topic": topic_in}

    except Exception as e:
        logger.error(f"Error executing start_workflow: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}
