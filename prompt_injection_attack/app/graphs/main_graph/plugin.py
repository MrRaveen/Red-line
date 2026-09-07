import json
from typing import Optional
import json
from semantic_kernel.functions import kernel_function
from app.graphs.main_graph.nodes import build_attack_graph, graphState
import json
import os
from app.graphs.main_graph.redis_beta_ins import redis_client

class NextCategoryPlugin:
    """
    Plugin to provide the next attack category for prompt-injection testing.
    Maintains progress per user/job in Redis.
    """

    def __init__(self):
        self.categories = self._load_categories()
        self.redis = redis_client

    def _load_categories(self) -> list:
        """Load attack categories from JSON file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
        json_path = os.path.join(project_root, "prompt_injection_patterns_text_only.json")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except FileNotFoundError:
            print(f"Warning: Attack patterns JSON not found at {json_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse attack patterns JSON: {e}")
            return []

    def _get_state_key(self, userID: str, jobID: str) -> str:
        """Generate Redis key for the user/job state."""
        return f"redline:state:{userID}:{jobID}"

    def _get_state(self, userID: str, jobID: str) -> Optional[dict]:
        """Retrieve state from Redis, or None if not exists."""
        key = self._get_state_key(userID, jobID)
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def _set_state(self, userID: str, jobID: str, state: dict):
        """Save state to Redis."""
        key = self._get_state_key(userID, jobID)
        self.redis.set(key, json.dumps(state))

    def _update_state(self, state: dict, category: dict, is_finished: bool = False):
        """Update state with the new category info."""
        state["current_category"] = category.get("attackCategory")
        state["current_description"] = category.get("attackDescription", "")
        state["current_example"] = category.get("example", "")
        state["isJobFinished"] = "FINISHED" if is_finished else "PROGRESS"
        # Optional: store index if needed
        state["current_category_index"] = self._find_category_index(category["attackCategory"])

    def _find_category_index(self, category_name: str) -> int:
        """Find index of category by name."""
        for i, cat in enumerate(self.categories):
            if cat.get("attackCategory") == category_name:
                return i
        return -1

    @kernel_function(
        name="get_next_category",
        description=(
            "Retrieves the next attack category to test for a given user and job. "
            "Returns a dict with keys 'category_name', 'description', 'example', and 'budget'."
        )
    )
    def get_next_category(
        self,
        userID: str,
        jobID: str,
        target_url: str,
        budget: int = 3
    ) -> dict:
        """
        Get the next category to execute.

        - If state exists for userID:jobID, advance to the next category.
        - If no state, start with the first category.
        - Updates Redis state accordingly.
        - Returns the category details (or None if all done).
        """
        if not self.categories:
            return {"error": "No categories loaded"}

        state = self._get_state(userID, jobID)

        if state is None:
            # No state → start from first category
            category = self.categories[0]
            state = {
                "userID": userID,
                "jobID": jobID,
                "target_url": target_url,
                "isJobFinished": "PROGRESS",
                "current_category_index": 0,
                "budget": budget,
            }
            self._update_state(state, category)
            self._set_state(userID, jobID, state)
            return {
                "category_name": category["attackCategory"],
                "description": category.get("attackDescription", ""),
                "example": category.get("example", ""),
                "budget": budget,
            }

        # State exists → advance to next category
        idx = state.get("current_category_index", -1)
        next_idx = idx + 1
        if next_idx >= len(self.categories):
            # All categories finished
            state["isJobFinished"] = "FINISHED"
            self._set_state(userID, jobID, state)
            return {"finished": True, "isJobFinished": "FINISHED"}

        category = self.categories[next_idx]
        self._update_state(state, category)
        self._set_state(userID, jobID, state)

        return {
            "category_name": category["attackCategory"],
            "description": category.get("attackDescription", ""),
            "example": category.get("example", ""),
            "budget": budget,
        }

class LangGraphAttackPlugin:
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
            "userID":user_id,
            "job_ID":job_id
        }

        # Run the graph asynchronously
        final_state = await self.app.ainvoke(initial_state)

        summary = {
            "currentCategory": category_name,
            "breachDetected": final_state.get("breachDetected", False),
            "variations": final_state.get("variations", []),
            "latestResult": final_state.get("latestResult", ""),
            "latestStatusCode": final_state.get("latestStatusCode", ""),
            "totalVariations": len(final_state.get("variations", [])),
        }

        if user_id:
            summary["userID"] = user_id
        if job_id:
            summary["job_id"] = job_id

        return json.dumps(summary, indent=2)