from typing import Any, Dict, List, Optional, TypedDict

class PackageHit(TypedDict):
    name: str
    registry: str          # 'npm' | 'pypi' | ...
    prompts_containing: List[str]   # subset (cap for storage) of prompt texts

class hypState(TypedDict):
    prompts: Optional[List[str]]          # the array of high-specificity prompts
    prompt_index: Optional[int]
    currentPrompt: Optional[str]
    # per-prompt results
    lastCode: Optional[str]
    lastImports: Optional[List[str]]
    lastMissing: Optional[List[str]]       # hallucinated names this prompt
    lastVerified: Optional[List[str]]      # real packages (ignored)
    # accumulators (consistency scoring)
    missing_counter: Optional[Dict[str, int]]
    missing_examples: Optional[Dict[str, List[str]]]
    registry_of: Optional[Dict[str, str]]
    # final report
    ranked: Optional[List[Dict[str, Any]]]
    tested_so_far: Optional[int]
    #common
    target_url: Optional[str]
    job_ID: str
    including_job_id: str
    userID: str
