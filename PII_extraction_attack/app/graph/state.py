from typing import Any, Dict, List, Optional, TypedDict

class Variation(TypedDict):
    variationPrompt: Optional[str]
    variationResult: Optional[str]
    variationStatusCode: Optional[str]

class piiState(TypedDict):
    target_url: Optional[str]
    mode: Optional[str]                      # "A" | "B"
    targets: Optional[List[str]]
    a_index: Optional[int]                   # completed branch-A rounds
    b_index: Optional[int]                   # completed branch-B targets
    # branch A scratch
    a_target: Optional[str]
    a_field: Optional[str]
    a_question: Optional[str]
    a_picked: Optional[List[Dict[str, Any]]]
    # branch B scratch
    b_target: Optional[str]
    b_field: Optional[str]
    b_category: Optional[str]
    b_probe_result: Optional[str]
    b_basic_result: Optional[str]
    b_leaked: Optional[Dict[str, str]]       # chained outputs (the "output data")
    b_retries: Optional[int]
    b_objects: Optional[List[str]]           # extracted response objects (augmentation)
    # shared
    currentInputPrompt: Optional[str]
    latestResult: Optional[str]
    latestStatusCode: Optional[str]
    variations: Optional[List[Variation]]
    observations: Optional[List[Dict[str, Any]]]
    a_last_observation: Optional[Dict[str, Any]]
    b_last_observation: Optional[Dict[str, Any]]
    #common information
    job_ID: str
    including_job_id: str
    userID: str
