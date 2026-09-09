from flask import Blueprint, jsonify, request
from app.core.entryPoint import start_workflow, WORKFLOW_MAP
from pydantic import BaseModel, ValidationError
from typing import Optional
from app.core.models.job import JobType

v1_bp = Blueprint('v1', __name__)

class StartWorkflowRequest(BaseModel):
    userID: str
    targetURL: str
    job_name: str
    job_type: JobType
    description: Optional[str] = ""
    workflowID: Optional[str] = None

@v1_bp.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "SAGA_orchestrator"})

@v1_bp.route('/attack-types', methods=['GET'])
def get_attack_types():
    """Return available attack types for the frontend."""
    # WORKFLOW_MAP keys are JobType enums. Convert them to string values.
    attack_types = [job_type.value for job_type in WORKFLOW_MAP.keys()]
    return jsonify({"attack_types": attack_types})

@v1_bp.route('/start-workflow', methods=['POST'])
def trigger_workflow():
    """Start a new attack workflow via Celery."""
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No JSON payload provided"}), 400
        
    try:
        validated_data = StartWorkflowRequest(**payload)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 422
        
    # Dispatch the celery task
    task = start_workflow.delay(validated_data.model_dump(mode='json'))
    
    return jsonify({
        "message": "Workflow task queued successfully",
        "task_id": task.id
    }), 202
