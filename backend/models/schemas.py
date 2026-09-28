from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime


class IncidentRequest(BaseModel):
    title: str = Field(..., min_length=3, description="Short title of the incident")
    service: str = Field(..., min_length=1, description="Affected service name")
    environment: str = Field(default="production", description="Environment: production, staging, dev")
    severity: str = Field(default="high", description="Severity: critical, high, medium, low")
    description: str = Field(..., min_length=10, description="Detailed description of the incident")
    logs: Optional[str] = Field(default="", description="Relevant error logs or output")
    recent_changes: Optional[str] = Field(default="", description="Recent deployments or changes")


class RecalledMemory(BaseModel):
    text: str
    relevance_note: Optional[str] = None


class MemoryRecallResult(BaseModel):
    found: bool
    memories: List[RecalledMemory] = []
    recall_query_used: str = ""


class IncidentAnalysis(BaseModel):
    summary: str
    investigation_steps: List[str] = []
    possible_causes: List[str] = []
    recommended_actions: List[str] = []
    memory_influenced: bool = False


class AnalyzeResponse(BaseModel):
    incident_id: str
    status: str = "analyzing"
    analysis: IncidentAnalysis
    memory_recall: MemoryRecallResult


class ResolveRequest(BaseModel):
    root_cause: str = Field(..., min_length=5, description="Actual root cause of the incident")
    fix: str = Field(..., min_length=5, description="Fix that was applied")
    outcome: str = Field(..., min_length=5, description="Result after the fix")
    resolution_time_minutes: Optional[int] = Field(default=None, description="How long resolution took in minutes")


class ResolveResponse(BaseModel):
    incident_id: str
    memory_stored: bool
    document_id: str
    message: str


class IncidentRecord(BaseModel):
    incident_id: str
    created_at: str
    request: IncidentRequest
    analysis: Optional[IncidentAnalysis] = None
    memory_recall: Optional[MemoryRecallResult] = None
    resolution: Optional[ResolveRequest] = None
    status: str = "open"
