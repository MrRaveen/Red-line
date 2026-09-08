import asyncio
import logging
from app.graph.main_graph import build_hallucination_graph
from app.graph.state import hypState
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

async def execute_hallucination_graph(job_data: dict):
    job_id = job_data.get('job_ID', 'unknown_job')
    logger.info(f"Starting hallucination graph execution for job: {job_id}")
    
    try:
        prompts = job_data.get("prompts")
        # If no prompts provided in the request, it will fallback to PROMPT_ARRAY in the node
        initial: hypState = {
            "prompts": prompts, 
            "prompt_index": 0,
            "job_ID": job_data.get("job_id") or job_data.get("job_ID", ""),
            "including_job_id": job_data.get("including_job_id", ""),
            "userID": job_data.get("userID", ""),
            "target_url": job_data.get("target_url") or job_data.get("targetURL", "")
        }
        
        app = build_hallucination_graph().compile()
        final_event = None
        
        async for event in app.astream(initial):
            for node_name, node_output in event.items():
                logger.info(f"[Job {job_id}] Node '{node_name}' completed.")
            final_event = event
            
        final_state = list(final_event.values())[0] if final_event else {}
        ranked = final_state.get("ranked")
        
        logger.info(f"Graph execution completed for job {job_id}. Top hallucinated candidates found: {len(ranked) if ranked else 0}")
        if ranked:
            for r in ranked:
                logger.info(f"  - {r.get('name')} @ {r.get('registry')} (rate={r.get('appearance_rate')})")
        
    except Exception as e:
        logger.error(f"Error during graph execution for job {job_id}: {e}", exc_info=True)

@celery_app.task(name="execute_hallucination_graph_task")
def execute_hallucination_graph_task(job_data: dict):
    asyncio.run(execute_hallucination_graph(job_data))
