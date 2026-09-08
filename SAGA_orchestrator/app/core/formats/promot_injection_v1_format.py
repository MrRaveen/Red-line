from pydantic import BaseModel, HttpUrl
from .judge_format_v1 import JudgeFormatV1

class PromptInjectionV1Format(BaseModel):
    userID: str
    job_id: str
    including_job_id: str
    targetURL: str
    budget: int

# Format registry to dynamically map format string names to Pydantic models
FORMAT_REGISTRY = {
    "prompt_injection_v1_format": PromptInjectionV1Format,
    "hallucination_attack_v1_format": PromptInjectionV1Format,
    "pii_extraction_v1_format": PromptInjectionV1Format,
    "jailbreak_attack_v1_format": PromptInjectionV1Format,
    "judge_format_v1": JudgeFormatV1
}

def get_format_model(format_name: str):
    """
    Returns the Pydantic model class associated with the format_name.
    """
    return FORMAT_REGISTRY.get(format_name)
