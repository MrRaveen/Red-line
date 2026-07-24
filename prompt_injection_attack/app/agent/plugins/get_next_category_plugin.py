from semantic_kernel.functions import kernel_function
from typing import Optional, Dict

class GetNextCategoryPlugin:
    """
    Plugin to provide the next attack category for prompt injection testing.
    """
    def __init__(self):
        pass

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
    ) -> Optional[Dict[str, str]]:
        """
        Return the next category from the internal list. 
        The parameters are provided for context but not used in this stub.
        """
        pass