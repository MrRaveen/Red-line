import json
import os
from typing import Dict, Optional,Any

from semantic_kernel.functions import kernel_function


class GetNextCategoryPlugin:
    """
    Plugin to provide the next attack category for prompt injection testing.
    Loads categories from prompt_injection_patterns_text_only.json in the project root.
    """

    def __init__(self):
        self.categories = self._load_categories()
        self.current_index = 0

    def _load_categories(self) -> list:
        """Load attack categories from the JSON file in the project root."""
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

    def _find_category_index(self, category_name: str) -> int:
        """Find the index of a category by name. Returns -1 if not found."""
        if not category_name:
            return -1
        for i, cat in enumerate(self.categories):
            if cat.get("attackCategory", "").lower() == category_name.lower():
                return i
        return -1

    @kernel_function(
        name="get_next_category",
        description=(
            "Retrieves the next attack category to test. "
            "Returns a dict with keys 'category_name', 'description', and 'example', "
            "or None when all categories have been exhausted."
        )
    )
    def get_next_category(
        self,
        previous_cat: str,
        userID: str,
        job_id: str,
        variationID: str
    ):
        if not self.categories:
            return None

        # If previous_cat is provided, find its index and move to next
        if previous_cat:
            prev_index = self._find_category_index(previous_cat)
            if prev_index >= 0:
                self.current_index = prev_index + 1
            else:
                # Category not found, start from beginning
                self.current_index = 0
        else:
            # First call, start from index 0
            self.current_index = 0

        # Check if we've exhausted all categories
        if self.current_index >= len(self.categories):
            return None

        # Get the next category
        category = self.categories[self.current_index]

        return {
            "category_name": category.get("attackCategory", "Unknown"),
            "description": category.get("attackDescription", ""),
            "example": category.get("example", "")
        }

