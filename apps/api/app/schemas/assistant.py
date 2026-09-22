from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AssistantQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Procurement or policy question")


class AssistantActionPreviewRequest(BaseModel):
    action_type: str = Field("DRAFT_PURCHASE_REQUEST", description="Action type to preview")
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5)
    category: str = Field("General", max_length=100)
    estimated_amount: float = Field(..., ge=0.0)
    department: Optional[str] = Field(None, max_length=100)
    suggested_vendor: Optional[str] = Field(None, max_length=255)


class AssistantQueryResponse(BaseModel):
    answer: str
    citations: List[str] = []
    tool_calls: List[Dict[str, Any]] = []
    action_proposals: List[Dict[str, Any]] = []
    model_version: str
    prompt_version: str
    latency_ms: int
    provider: str


class AssistantActionPreviewResponse(BaseModel):
    action_type: str
    is_executable: bool
    draft_data: Dict[str, Any]
    compliance_note: str
