import json
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def get_next_step(workflow_id: str, current_step_name: str) -> Optional[Dict]:
    """
    Reads the workflow JSON and returns the step immediately following current_step_name.
    Returns None if the current step is the last step or not found.
    """
    workflow_path = os.path.join(os.path.dirname(__file__), f"../workflows/{workflow_id}.JSON")
    if not os.path.exists(workflow_path):
        logger.error(f"Workflow file not found: {workflow_path}")
        return None
        
    with open(workflow_path, 'r') as f:
        workflow_data = json.load(f)
        
    steps = workflow_data.get("steps", [])
    for i, step in enumerate(steps):
        if step.get("name") == current_step_name:
            # Check if there is a next step
            if i + 1 < len(steps):
                return steps[i + 1]
            else:
                return None
                
    logger.warning(f"Step '{current_step_name}' not found in workflow '{workflow_id}'")
    return None
