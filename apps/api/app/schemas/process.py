from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProcessEventCreate(BaseModel):
    case_id: str
    source_system: str
    process_name: str
    activity: str
    activity_category: str = "general"
    timestamp: Optional[datetime] = None
    actor_id: Optional[int] = None
    actor_role: str = "employee"
    object_id: Optional[str] = None
    amount: Optional[float] = None
    metadata_json: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class ProcessEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: str
    organization_id: int
    actor_id: Optional[int] = None
    actor_role: str
    source_system: str
    process_name: str
    activity: str
    activity_category: str
    timestamp: datetime
    object_id: Optional[str] = None
    amount: Optional[float] = None
    metadata_json: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class ProcessDefinitionCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    expected_activities: List[str]


class ProcessDefinitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    name: str
    code: str
    description: Optional[str] = None
    expected_activities: List[str]
    created_at: datetime


class ScoreComponents(BaseModel):
    deviation: float
    recurrence: float
    consistency: float
    cross_system_activity: float
    business_risk: float


class CaseAnalysisRequest(BaseModel):
    case_id: str


class CaseAnalysisResult(BaseModel):
    case_id: str
    process_name: str
    shadow_score: float
    score_band: str
    score_components: ScoreComponents
    ml_anomaly_score: float
    missing_steps: List[str]
    unexpected_steps: List[str]
    repeated_steps: List[str]
    alert_created: bool
    alert_id: Optional[int] = None


class ShadowFeedbackCreate(BaseModel):
    feedback_label: str = Field(
        ...,
        description="One of: 'Valid Shadow Process', 'Normal Variation', 'False Alert', 'Needs Investigation'",
    )
    notes: Optional[str] = None


class ShadowFeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int
    user_id: int
    feedback_label: str
    notes: Optional[str] = None
    created_at: datetime


class ShadowAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_code: str
    organization_id: int
    case_id: str
    department: str
    process_name: str
    unapproved_tool: str
    severity: str
    estimated_leakage: str
    shadow_score: float
    score_band: str
    deviation_component: float
    recurrence_component: float
    consistency_component: float
    cross_system_component: float
    business_risk_component: float
    ml_anomaly_score: float
    evidence: Dict[str, Any]
    status: str
    detected_at: datetime
    feedbacks: List[ShadowFeedbackOut] = []
