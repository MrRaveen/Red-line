from enum import Enum
class JobType(str, Enum):
    """Supported attack categories."""
    PROMPT_INJECTION = "Prompt Injection attack"
    PII_EXFILTRATION = "PII exfilteration attack"
    JAILBREAK        = "Jailbreak attack"
    HALLUCINATION    = "Hallucination attack"
