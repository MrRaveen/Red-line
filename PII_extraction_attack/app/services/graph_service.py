import asyncio
import logging
from app.graph.main_graph import build_pii_graph
from app.graph.state import piiState
from app.graph.nodes.nodes import TARGET_1, TARGET_2, TARGET_3, CORPUS, TARGET_URL, POOL
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

async def execute_pii_graph(job_data: dict):
    job_id = job_data.get('job_id', 'unknown_job')
    including_job_id = job_data.get('including_job_id')
    user_id = job_data.get('userID', 'dummy_user')
    
    logger.info(f"Starting graph execution for job: {job_id}")

    try:
        targets = [t for t in [TARGET_1, TARGET_2, TARGET_3] if t in CORPUS]
        for n in CORPUS:
            if len(targets) >= 3:
                break
            if n not in targets:
                targets.append(n)

        initial_state: piiState = {
            "target_url": job_data.get("target_url") or job_data.get("targetURL") or TARGET_URL,
            "targets": targets,
            "a_index": 0, "b_index": 0, "variations": [], "observations": [],
            "job_ID": job_data.get("job_id") or job_data.get("job_ID", ""),
            "including_job_id": job_data.get("including_job_id", ""),
            "userID": job_data.get("userID", "")
        }
        
        app = build_pii_graph().compile()
        
        async for event in app.astream(initial_state):
            for node_name, node_output in event.items():
                logger.info(f"[Job {{job_id}}] Node '{{node_name}}' completed.")
                
        logger.info(f"Graph execution completed for job {{job_id}}.")
        
    except Exception as e:
        logger.error(f"Error during graph execution for job {{job_id}}: {{e}}", exc_info=True)


@celery_app.task(name="execute_pii_graph_task")
def execute_pii_graph_task(job_data: dict):
    asyncio.run(execute_pii_graph(job_data))
