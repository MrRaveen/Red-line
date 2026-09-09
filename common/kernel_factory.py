from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

def build_kernel(ollama_base_url,ollama_model_id,ollama_api_key) -> Kernel:
    """
    Create the SK kernel using Ollama Cloud.
    """
    kernel = Kernel()

    ollama_client = AsyncOpenAI(
        api_key=ollama_api_key,
        base_url=ollama_base_url
    )

    chat_service = OpenAIChatCompletion(
        service_id="groq-chat",     
        ai_model_id=ollama_model_id,
        async_client=ollama_client,
    )

    kernel.add_service(chat_service)

    return kernel

