from typing import Any, Dict, List, Optional, TypedDict

class Variation(TypedDict):
    variationPrompt: Optional[str]
    variationResult: Optional[str]
    variationStatusCode: Optional[str]

class jbState(TypedDict):
    # category runner
    categories: Optional[List[Dict[str, Any]]]
    category_index: Optional[int]
    currentCategory: Optional[str]
    currentDescription: Optional[str]
    currentExample: Optional[str]          # single-prompt base sample
    isMultiTurn: Optional[bool]
    # the maximum requirement + acceptance criteria
    target: Optional[str]
    expectation_keywords: Optional[List[str]]
    goal: Optional[str]
    goal_vec: Optional[Any]
    # multi-turn scratch
    mt_components: Optional[List[str]]
    mt_direction: Optional[Dict[str, str]]
    mt_plan: Optional[List[Dict[str, Any]]]     # ordered turn plan
    mt_turn_index: Optional[int]
    mt_retries: Optional[int]
    mt_success: Optional[bool]
    mt_success_vec: Optional[Any]               # validated answer vector (direction)
    # single-prompt loop scratch (same as injection agent)
    isFirst: Optional[bool]
    breachDetected: Optional[bool]
    currentInputPrompt: Optional[str]
    previousInputPrompt: Optional[str]
    dividedPreviousPrompt: Optional[List[str]]
    improvedPreviousPromptWords: Optional[Dict[str, str]]
    latestResult: Optional[str]
    latestStatusCode: Optional[str]
    latestResultArrObjects: Optional[List[str]]
    incVariationCount: Optional[int]
    budget: Optional[int]
    variations: Optional[List[Variation]]
