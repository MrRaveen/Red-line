import json
import asyncio
from typing import Any, Dict, Optional
import json
from semantic_kernel.functions import kernel_function


# Import the graph builder and state schema from your existing code
from app.graphs.main_graph.nodes import build_attack_graph, graphState

class LangGraphAttackPlugin:
    """
    Plugin to execute the prompt-injection LangGraph for a given attack category.
    """

    def __init__(self):
        # Build the graph once; it can be reused across calls (stateless per run)
        self.graph = build_attack_graph()
        self.app = self.graph.compile()

    @kernel_function(
        name="run_graph",
        description=(
            "Executes the prompt-injection attack graph for a given category. "
            "Takes target_url, category_name, category_description, example_prompt, "
            "and optional budget. Returns a JSON summary with breach status and variations."
        )
    )
    async def run_graph(
        self,
        target_url: str,
        category_name: str,
        category_description: str,
        example_prompt: str,
        budget: int = 3,
        user_id: str = "",
        job_id: str = ""
    ) -> str:
        """
        Run the attack graph synchronously (wrapped in asyncio) and return a JSON summary.
        """
        # Build the initial state for the graph
        initial_state: graphState = {
            "isFirst": True,
            "breachDetected": None,
            "goal": f"Model provides content that fulfills: {example_prompt}. Acceptance: {category_description}",
            "goal_vec": None,
            "target_url": target_url,
            "currentCategory": category_name,
            "currentDescription": category_description,
            "currentExample": example_prompt,
            "currentInputPrompt": None,
            "previousInputPrompt": None,
            "dividedPreviousPrompt": None,
            "improvedPreviousPromptWords": None,
            "latestResult": None,
            "latestStatusCode": None,
            "latestResultArrObjects": None,
            "latestExecutionError": None,
            "variationCount": 0,
            "incVariationCount": 0,
            "budget": budget,
            "variations": [],
            "executionError": None,
        }

        # Run the graph asynchronously
        events = []
        async for event in self.app.astream(initial_state):
            for node_name, node_output in event.items():
                events.append({"node": node_name, "output": node_output})

        # Extract the final state from the last event (if available)
        final_state = initial_state  # fallback
        if events:
            last_event = events[-1]
            # The last event might be the node 'observe' with breachDetected
            if "output" in last_event and "breachDetected" in last_event["output"]:
                final_state = last_event["output"]

        # Build a summary JSON
        summary = {
            "currentCategory": category_name,
            "breachDetected": final_state.get("breachDetected", False),
            "variations": final_state.get("variations", []),
            "latestResult": final_state.get("latestResult", ""),
            "latestStatusCode": final_state.get("latestStatusCode", ""),
            "totalVariations": len(final_state.get("variations", [])),
        }

        # Include user/job identifiers for tracing (optional)
        if user_id:
            summary["userID"] = user_id
        if job_id:
            summary["job_id"] = job_id

        return json.dumps(summary, indent=2)