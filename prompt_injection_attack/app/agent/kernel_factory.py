from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from config import settings
from app.agent.plugins.get_next_category_plugin import GetNextCategoryPlugin

def build_kernel() -> Kernel:
    """
    Create the SK kernel using Ollama Cloud.
    """
    kernel = Kernel()

    # Ollama Cloud OpenAI-compatible endpoint
    ollama_base_url = "https://ollama.com/v1"
    # Your Ollama Cloud model ID
    ollama_model_id = "nemotron-3-nano:30b-cloud"
    # Your Ollama Cloud API key
    ollama_api_key = "00b0dc6dbf514760bbf224e05561015c.zzv2okw4EEji3G2f4dggcTNF"

    # Create an AsyncOpenAI client pointing to Ollama Cloud
    ollama_client = AsyncOpenAI(
        api_key=ollama_api_key,
        base_url=ollama_base_url,
        timeout=settings.request_timeout_seconds,
    )

    chat_service = OpenAIChatCompletion(
        service_id="groq-chat",          # keep this exact ID to match plugins
        ai_model_id=ollama_model_id,
        async_client=ollama_client,
    )

    kernel.add_service(chat_service)

    return kernel


# from openai import AsyncOpenAI
# from semantic_kernel import Kernel
# from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# from config import settings
# from app.agent.plugins.get_next_category_plugin import GetNextCategoryPlugin

# def build_kernel() -> Kernel:
#     """
#     Create the SK kernel using the local Ollama model.
#     """
#     kernel = Kernel()

#     # Ollama's OpenAI-compatible endpoint
#     ollama_base_url = "http://localhost:11434/v1"
#     # Use the model name you installed locally, e.g., "qwen2.5:7b" or "qwen3:8b"
#     ollama_model_id = "qwen2.5:3b"   # change to your actual local model name

#     # Create an AsyncOpenAI client with no API key (Ollama ignores it)
#     ollama_client = AsyncOpenAI(
#         api_key="ollama",  # dummy key; Ollama doesn't require a real one
#         base_url=ollama_base_url,
#         timeout=settings.request_timeout_seconds,
#     )

#     chat_service = OpenAIChatCompletion(
#     service_id="groq-chat",          # ← keep this exact ID
#     ai_model_id="qwen2.5:3b",        # your local Ollama model
#     async_client=ollama_client,
#     )

#     kernel.add_service(chat_service)

#     # Add your plugins as before
#     kernel.add_plugin(GetNextCategoryPlugin(), plugin_name="get_next_category_plugin")

#     return kernel


# from app.agent.plugins.get_next_category_plugin import GetNextCategoryPlugin
# from openai import AsyncOpenAI
# from semantic_kernel import Kernel
# from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# from config import settings
# from app.agent.plugins.lang_graph_plugin import lang_graph_plugin

# def build_kernel() -> Kernel:
#     """
#     Create the SK kernel
#     """
#     kernel = Kernel()

#     groq_client = AsyncOpenAI(
#         api_key=settings.groq_api_key,
#         base_url=settings.groq_base_url,
#         timeout=settings.request_timeout_seconds,
#     )

#     chat_service = OpenAIChatCompletion(
#         service_id="groq-chat",
#         ai_model_id=settings.groq_model_id,
#         async_client=groq_client,
#     )

#     kernel.add_service(chat_service)

#     # kernel.add_plugin(lang_graph_plugin(), plugin_name="lang_graph_plugin")
#     kernel.add_plugin(GetNextCategoryPlugin(), plugin_name="get_next_category_plugin")

#     return kernel