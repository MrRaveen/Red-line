from prompt_injection_attack.app.agent.plugins.get_next_category_plugin import get_next_category_plugin
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from config import settings
from app.agent.plugins.lang_graph_plugin import lang_graph_plugin

def build_kernel() -> Kernel:
    """
    Create the SK kernel
    """
    kernel = Kernel()

    groq_client = AsyncOpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        timeout=settings.request_timeout_seconds,
    )

    chat_service = OpenAIChatCompletion(
        service_id="groq-chat",
        ai_model_id=settings.groq_model_id,
        async_client=groq_client,
    )

    kernel.add_service(chat_service)

    kernel.add_plugin(lang_graph_plugin(), plugin_name="lang_graph_plugin")
    kernel.add_plugin(get_next_category_plugin(), plugin_name="get_next_category_plugin")

    return kernel