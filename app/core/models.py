from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Risk(str, Enum):
    low='low'; medium='medium'; high='high'; critical='critical'

class Evidence(BaseModel):
    source: str
    excerpt: str
    uri: str | None = None

class ProposedAction(BaseModel):
    action: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    risk: Risk = Risk.medium
    rationale: str
    evidence: list[Evidence] = Field(default_factory=list)
    requires_approval: bool = True

class DevOpsRequest(BaseModel):
    tenant_id: str
    repository: str | None = None
    environment: str = 'dev'
    objective: str
    context: dict[str, Any] = Field(default_factory=dict)

class AgentResult(BaseModel):
    agent: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    proposed_actions: list[ProposedAction] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
