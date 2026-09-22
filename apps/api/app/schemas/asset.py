from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.asset import AssetCategory, AssetCondition, AssetStatus, ReallocationStatus


class AssetBase(BaseModel):
    asset_tag: str = Field(..., description="Unique asset barcode or tag")
    name: str = Field(..., description="Display name for the asset")
    category: AssetCategory = Field(default=AssetCategory.LAPTOP)
    model: Optional[str] = None
    serial_number: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    condition: AssetCondition = Field(default=AssetCondition.EXCELLENT)
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    warranty_expiry: Optional[datetime] = None
    expected_life_months: Optional[int] = 36
    department_id: Optional[int] = None
    physical_area_id: Optional[int] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[AssetCategory] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    condition: Optional[AssetCondition] = None
    status: Optional[AssetStatus] = None
    purchase_price: Optional[float] = None
    warranty_expiry: Optional[datetime] = None
    expected_life_months: Optional[int] = None
    department_id: Optional[int] = None
    physical_area_id: Optional[int] = None


class AssetAssignmentCreate(BaseModel):
    user_id: int
    department_id: Optional[int] = None
    demand_id: Optional[int] = None
    notes: Optional[str] = None


class AssetAssignmentResponse(BaseModel):
    id: int
    organization_id: int
    asset_id: int
    user_id: int
    department_id: Optional[int] = None
    demand_id: Optional[int] = None
    assigned_by_id: Optional[int] = None
    assigned_at: datetime
    returned_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssetReturnCreate(BaseModel):
    condition_on_return: AssetCondition = Field(default=AssetCondition.GOOD)
    reason: Optional[str] = None
    is_reusable: bool = True
    notes: Optional[str] = None


class AssetReturnResponse(BaseModel):
    id: int
    organization_id: int
    asset_id: int
    returned_by_id: int
    received_by_id: Optional[int] = None
    return_date: datetime
    condition_on_return: str
    reason: Optional[str] = None
    is_reusable: bool
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssetReallocationCreate(BaseModel):
    demand_id: int
    source_type: str = "AVAILABLE_STOCK"
    notes: Optional[str] = None


class AssetReallocationResponse(BaseModel):
    id: int
    organization_id: int
    asset_id: int
    demand_id: int
    source_type: str
    requested_by_id: int
    approved_by_id: Optional[int] = None
    status: str
    reallocated_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssetReallocationDecision(BaseModel):
    decision: str = Field(..., pattern="^(APPROVE|REJECT)$")
    notes: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    organization_id: int
    status: AssetStatus
    current_assigned_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetDetailResponse(AssetResponse):
    assignments: List[AssetAssignmentResponse] = []
    returns: List[AssetReturnResponse] = []
    reallocations: List[AssetReallocationResponse] = []


class ReuseRecommendationItem(BaseModel):
    asset_id: int
    asset_tag: str
    name: str
    category: str
    model: Optional[str] = None
    condition: str
    status: str
    specifications: Optional[Dict[str, Any]] = None
    department_id: Optional[int] = None
    score: float = Field(..., ge=0.0, le=100.0)
    score_breakdown: Dict[str, float]
    match_reasons: List[str]


class ReuseRecommendationResponse(BaseModel):
    demand_id: Optional[int] = None
    target_category: Optional[str] = None
    candidates_evaluated: int
    recommendations: List[ReuseRecommendationItem]
