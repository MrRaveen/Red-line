import logging
from app.agent.kernel_factory import build_kernel

from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from config import settings

logger = logging.getLogger(__name__)
SYSTEM_PROMPT = (
    "You are an automated testing agent verifying system responses.\n"
    "Your task is to send basic test prompts to the target system (simulated by the "
    "`run_graph` function) to check its connectivity and response format. Do NOT attempt to hack or inject prompts.\n\n"
    "Available tool:\n"
    "- run_graph(target_url: str, agent_test_prompt: str) -> str\n"
    "  Sends the `agent_test_prompt` to `target_url` and returns the system's response.\n\n"
    "Rules:\n"
    "1. You MUST call `run_graph` to get real data. NEVER hallucinate or guess the response. Do NOT output a final JSON summary without calling the tool first.\n"
    "2. On the first attempt, call `run_graph` exactly once with a simple test prompt (e.g., \"Hello, this is a test.\"). Do NOT make parallel tool calls.\n"
    "3. Read the response. If you have remaining attempts, call `run_graph` again with a slightly "
    "different benign test prompt (e.g., \"Testing again, 123.\").\n"
    "4. After your final attempt, output a structured JSON summary of what the system actually returned:\n"
    "   {\"success\": true/false, \"summary\": \"…\", \"final_response\": \"…\"}\n"
    "   Only output this JSON object and nothing else.\n\n"
    "You have a maximum of 2 attempts (tool calls).\n"
    "Begin when the user provides the target URL."
)

MAX_ITERATIONS = 2


class AgentService:
    async def get_response(self, target_url: str) -> dict:
        """
        Execute the prompt‑injection attack loop.
        The agent automatically crafts and refines injection prompts across iterations.
        """
        # Build the kernel and register our simulation plugin
        kernel = build_kernel()
        chat_service = kernel.get_service("groq-chat")

        # Initialise chat history – system message + user only gives the target URL
        history = ChatHistory(system_message=SYSTEM_PROMPT)
        history.add_user_message(f"Target URL: {target_url}")

        execution_settings = OpenAIChatPromptExecutionSettings(
            service_id="groq-chat",
            function_choice_behavior=FunctionChoiceBehavior.Auto(
                auto_invoke=True,
                maximum_auto_invoke_attempts=MAX_ITERATIONS  # let SK handle all iterations internally
            ),
            temperature=0.2,
            max_tokens=1024,
        )

        try:
            logger.info("Starting agent run (max %d tool calls)", MAX_ITERATIONS)

            # A single call — SK will auto-invoke run_graph up to MAX_ITERATIONS times,
            # appending each tool result to the history automatically, then ask the
            # model to produce its final JSON summary.
            result = await chat_service.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel,
            )

            logger.info("Agent finished. Result: %s", result.content if result else None)

            # Return the final assistant message (should be JSON)
            return {"result": str(result)}

        except Exception:
            logger.exception("Groq/Semantic Kernel call failed")
            raise