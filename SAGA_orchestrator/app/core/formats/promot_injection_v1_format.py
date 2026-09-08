from pydantic import BaseModel, HttpUrl

class PromptInjectionV1Format(BaseModel):
    userID: str
    job_id: str
    including_job_id: str
    targetURL: str

# Format registry to dynamically map format string names to Pydantic models
FORMAT_REGISTRY = {
    "prompt_injection_v1_format": PromptInjectionV1Format
}

def get_format_model(format_name: str):
    """
    Returns the Pydantic model class associated with the format_name.
    """
    return FORMAT_REGISTRY.get(format_name)
