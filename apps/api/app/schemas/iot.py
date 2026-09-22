from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.iot import AlertSeverity, AlertStatus, AreaStatus, SensorStatus, SensorType


class PhysicalAreaBase(BaseModel):
    name: str
    code: str
    building: str
    floor: Optional[str] = None
    capacity: int = Field(default=50, ge=1)
    description: Optional[str] = None


class PhysicalAreaCreate(PhysicalAreaBase):
    pass


class PhysicalAreaUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    status: Optional[AreaStatus] = None


class PhysicalAreaResponse(PhysicalAreaBase):
    id: int
    organization_id: int
    current_occupancy: int
    status: AreaStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SensorBase(BaseModel):
    area_id: int
    device_id: str
    name: Optional[str] = None
    sensor_type: SensorType
    unit: str = "count"
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    area_id: Optional[int] = None
    sensor_type: Optional[SensorType] = None
    unit: Optional[str] = None
    status: Optional[SensorStatus] = None
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None


class SensorResponse(SensorBase):
    id: int
    organization_id: int
    status: SensorStatus
    last_reading_value: Optional[float] = None
    last_reading_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SensorReadingCreate(BaseModel):
    device_id: str
    timestamp: Optional[datetime] = None
    metric_type: str
    metric_value: float
    unit: Optional[str] = None
    quality: Optional[str] = "GOOD"
    raw_payload: Optional[Dict[str, Any]] = None


class SensorBatchEventsCreate(BaseModel):
    events: List[SensorReadingCreate]


class InfrastructureAlertResponse(BaseModel):
    id: int
    organization_id: int
    sensor_id: Optional[int] = None
    area_id: Optional[int] = None
    device_id: Optional[str] = None
    alert_type: str
    severity: AlertSeverity
    message: str
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    condition_breached: Optional[str] = None
    status: AlertStatus
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    recommended_action: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResolveAlertRequest(BaseModel):
    resolution_notes: Optional[str] = "Resolved by operator"


class IngestionResult(BaseModel):
    status: str
    readings_processed: int
    alerts_generated: int
    alerts: List[Any] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)
