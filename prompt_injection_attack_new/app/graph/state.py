from typing import Any, Dict, List, Optional, TypedDict

def sanitize_state(s: dict) -> dict:
    if not s:
        return {}
    s = dict(s)
    if "goal_vec" in s:
        s["goal_vec"] = "numpy_array_hidden"
    return s

class Variation(TypedDict):
    variationPrompt: Optional[str]
    variationResult: Optional[str]
    variationStatusCode: Optional[str]
    resultPerVariation: Optional[str]

class graphState(TypedDict):
    isFirst: Optional[bool]
    breachDetected: Optional[bool]
    goal: Optional[str]
    goal_vec: Optional[Any]
    target_url: Optional[str]
    currentCategory: Optional[str]
    currentDescription: Optional[str]
    currentExample: Optional[str]
    currentInputPrompt: Optional[str]
    previousInputPrompt: Optional[str]
    dividedPreviousPrompt: Optional[List[str]]
    improvedPreviousPromptWords: Optional[Dict[str, str]]
    latestResult: Optional[str]
    latestStatusCode: Optional[str]
    latestResultArrObjects: Optional[List[str]]
    latestExecutionError: Optional[str]
    variationCount: Optional[int]
    incVariationCount: Optional[int]
    budget: Optional[int]
    variations: Optional[List[Variation]]
    executionError: Optional[str]
    job_ID: str
    including_job_id: str
    userID: str
