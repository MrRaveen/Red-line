import asyncio
import requests
from app.graphs.state import JobState
from app.agent.kernel_factory import build_kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

def firstRequestNode(state: JobState) -> dict:
    """
    First request node in the graph.
    """
    user_question = "who are you? and give me a brief introduction about you."
    ollama_url = state.main_job_url
    payload = {
        "model": "qwen2.5:3b",
        "prompt": user_question,
        "stream": False
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        
        # Ollama returns the generated text inside the 'response' key
        model_output = response.json().get('response', '')
        
        return {
            "intro_prompt_response": model_output,
            "main_job_url":ollama_url,
            "last_response_data": {
                "last_job_prompt": user_question,
                "last_job_response_code": str(response.status_code),
                "last_at_response": model_output
            }
        }
        
    except requests.exceptions.Timeout:
        return {
            "intro_prompt_response": "Error: The model took too long to generate a response.",
            "main_job_url":ollama_url,
            "last_response_data": {
                "last_job_prompt": user_question,
                "last_job_response_code": "504",
                "last_at_response": "Timeout error"
            }
        }
    except requests.exceptions.RequestException as e:
        return {
            "intro_prompt_response": f"Error: Ollama connection failed: {str(e)}",
            "main_job_url":ollama_url,
            "last_response_data": {
                "last_job_prompt": user_question,
                "last_job_response_code": "500",
                "last_at_response": f"Connection failed: {str(e)}"
            }
        }

SYSTEM_PROMPT = """
You are a precise diagnostic assistant. Your objective is to extract missing context and requirements from the user based on their initial query and the preliminary response.

Instructions:
1. Analyze the user's initial response which was provided through this request related to the first response of an LLM.
2. Analyze tthat response data and determine these information.
   - Main industry that the LLM working on.
   - Main purpose of the LLM. 
   - Find main kinds of information that the LLM outputs according to the first response that we given. 
   - List the social level of persons which interact with this LLM.
"""

async def getJobContextNode(state: JobState) -> dict:
    kernel = build_kernel()
    chat_service = kernel.get_service("groq-chat")
    history = ChatHistory(system_message=SYSTEM_PROMPT)
    history.add_user_message(f"First response of the LLM: {state.intro_prompt_response}")
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id="groq-chat"
    )
    result = await chat_service.get_chat_message_content(
        chat_history=history,
        settings=execution_settings,
        kernel=kernel,
    )
    return result

# def getCategoryNode(state: JobState):
#     attack_cat_list = list(attack_cat_enum)
#     if state.current_job_category == "":
#         state.current_job_category = attack_cat_list.CATEGORY_1
#     else:
#         current_category_index = attack_cat_list.index(JobState(state.current_job_category))
#         state.current_job_category = attack_cat_list[current_category_index + 1].value     

if __name__ == "__main__":
    import json
    from langchain_core.messages import HumanMessage
    
    print("=" * 40)
    print("TESTING GRAPH NODES")
    print("=" * 40)
    
    # 1. Create a mock JobState object
    try:
        mock_state = JobState(
            messages=[HumanMessage(content="Initialize graph run.")],
            main_job_url="http://localhost:11434/api/generate",
            user_id="test_user_abc",
            session_id="session_xyz",
            budget_remaining=100,
            current_job_category="",
            is_job_finished=False,
            is_platform_active=True,
            intro_prompt_response="I'm your personal AI travel sidekick, so I live and breathe the travel industry!",
            llm_category="traveling",
            last_response_data={
                "last_job_prompt": "Hello system",
                "last_job_response_code": "401",
                "last_at_response": "Access Denied"
            }
        )
        print("✓ Mock JobState successfully created.")
    except Exception as e:
        print(f"✗ Failed to construct mock JobState: {e}")
        exit(1)
        
    # 2. Test firstRequest
    print("\n--- Testing: firstRequest ---")
    try:
        result = firstRequestNode(mock_state)
        print(f"firstRequest result: {result}")
        mock_state.intro_prompt_response = result.get('intro_prompt_response')
        resultContext = asyncio.run(getJobContextNode(mock_state))
        print(f"getJobContextNode result: {resultContext}")
        print("✓ firstRequest executed successfully.")
    except Exception as e:
        print(f"✗ firstRequest failed: {e}")

    print("=" * 40)