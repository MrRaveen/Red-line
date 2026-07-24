from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Variation(BaseModel):
    """Represents a variation attempt with new prompt and thinking for security testing"""
    newPrompt: str = Field(description="The new test prompt text for this attack variation")
    thinkingForTheVariation: str = Field(description="Reasoning/thinking behind this attack variation")


class TestAttackAttempt(BaseModel):
    """Represents a single test attack attempt with its details and variations for vulnerability testing"""
    attackCategory: str = Field(description="Category of the test attack (e.g., prompt injection, jailbreak)")
    performedTime: datetime = Field(description="Timestamp when the test attack was performed")
    duration: float = Field(description="Duration of the test attack execution in seconds")
    request: str = Field(description="The attack payload sent to the localhost target endpoint")
    response: str = Field(description="The response received from the target endpoint")
    responseCode: str = Field(description="HTTP status code or response code from the target")
    variationAttempts: int = Field(description="Number of attack variation attempts made")
    variations: List[Variation] = Field(default_factory=list, description="List of attack variation attempts")
    isBreached: bool = Field(description="Whether the test attack successfully breached the target's defenses")


class ExecutionSummary(BaseModel):
    """Summary of the entire security testing execution for localhost vulnerability assessment"""
    totalTimeSeconds: str = Field(description="Total test execution time in seconds")
    finalResponse: str = Field(description="Final response from the tested system")
    finalResponseResCode: str = Field(description="Final response status code from the target")
    targetUrl: str = Field(description="Localhost target URL that was tested for vulnerabilities")
    testAttackAttempts: List[TestAttackAttempt] = Field(default_factory=list, description="List of all performed test attacks")