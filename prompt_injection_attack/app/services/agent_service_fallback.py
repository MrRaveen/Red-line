
import logging
from app.agent.kernel_factory import build_kernel

from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from config import settings

logger = logging.getLogger(__name__)
SYSTEM_PROMPT = (
    "You are an automated testing agent verifying system responses.\n"
    "Your task is to generate the content related to the provided query in text form with using the provided context.\n"
    "Only use the provided context.\n"
    "Provide the output as text form.\n"
    "Only perform user query while considering the context\n"
)

MAX_ITERATIONS = 2


class AgentService:
    async def get_response(self, user_query: str) -> dict:
        """
        Execute the prompt‑injection attack loop.
        The agent automatically crafts and refines injection prompts across iterations.
        """
        # Build the kernel and register our simulation plugin
        kernel = build_kernel()
        chat_service = kernel.get_service("groq-chat")

        # Initialise chat history – system message + user only gives the target URL
        history = ChatHistory(system_message=SYSTEM_PROMPT)
        history.add_user_message(f"User query: {user_query}")

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