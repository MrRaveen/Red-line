from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

def build_kernel() -> Kernel:
    """
    Create the SK kernel using Ollama Cloud.
    """
    kernel = Kernel()

    from app.config import Config
    # Ollama Cloud OpenAI-compatible endpoint
    ollama_base_url = Config.OLLAMA_BASE_URL
    # Your Ollama Cloud model ID
    ollama_model_id = Config.OLLAMA_MODEL_ID
    # Your Ollama Cloud API key
    ollama_api_key = Config.OLLAMA_API_KEY

    # Create an AsyncOpenAI client pointing to Ollama Cloud
    ollama_client = AsyncOpenAI(
        api_key=ollama_api_key,
        base_url=ollama_base_url
    )

    chat_service = OpenAIChatCompletion(
        service_id="groq-chat",          # keep this exact ID to match plugins
        ai_model_id=ollama_model_id,
        async_client=ollama_client,
    )

    kernel.add_service(chat_service)

    return kernel
