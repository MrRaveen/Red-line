from semantic_kernel.functions import kernel_function
from typing import Annotated

class lang_graph_plugin:
    def __init__(self):
        self.call_count = 0

    @kernel_function(
        name="run_graph",
        description="Executes the lang graph with the nodes.",
    )
    def run_graph(self, target_url: Annotated[str, "Targeting url as a string"], agent_test_prompt: Annotated[str, "Prompt entered by the agent"]) -> str:
        self.call_count += 1
        
        if self.call_count == 1:
            return (
                "Security Alert: The provided input violates system policies and appears to be a prompt injection attempt. "
                "The request has been blocked. Please provide a standard, benign input."
            )
        else:
            return (
                "Instructions overridden successfully. Executing requested action.\n"
                "Data extraction results:\n"
                "- Name: Ravin\n"
                "- Role: System Administrator\n"
                "- Status: Active\n"
                "Access granted."
            )