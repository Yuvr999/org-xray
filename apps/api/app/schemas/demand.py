from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.models.demand import DemandStatus, ApprovalStatus, RoutingMethod


class DemandBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    category: str = "General"
    estimated_amount: float = Field(0.0, ge=0.0)


class DemandCreate(DemandBase):
    department_id: Optional[int] = None


class DemandUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    estimated_amount: Optional[float] = None
    department_id: Optional[int] = None


class ClassificationResult(BaseModel):
    demand_id: int
    routed_department: str
    confidence: float
    method: RoutingMethod
    explanation: str


class ApprovalDecision(BaseModel):
    comments: Optional[str] = None


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    demand_id: int
    approver_id: Optional[int] = None
    status: ApprovalStatus
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DemandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    requester_id: int
    department_id: Optional[int] = None
    title: str
    description: str
    category: str
    estimated_amount: float
    status: DemandStatus
    routed_department: Optional[str] = None
    routing_confidence: Optional[float] = None
    routing_method: Optional[RoutingMethod] = None
    routing_explanation: Optional[str] = None
    matched_asset_id: Optional[int] = None
    ai_recommendation: Optional[str] = None
    suggested_action: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    approvals: List[ApprovalOut] = []
