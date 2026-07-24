from typing import Annotated, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

class LastResponseData(BaseModel):
    last_job_prompt: str
    last_job_response_code: str
    last_at_response: str

class JobState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    main_job_url: str
    user_id: str
    session_id: str
    budget_remaining: int
    current_job_category: str
    is_job_finished: bool
    is_platform_active: bool
    intro_prompt_response: str
    llm_category: str
    last_response_data: LastResponseData
    model_config = {"arbitrary_types_allowed": True}