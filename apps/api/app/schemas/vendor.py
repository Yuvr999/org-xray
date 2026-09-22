from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VendorBase(BaseModel):
    name: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    region: str = Field("National", max_length=100)
    contact_email: Optional[EmailStr] = None
    rating: float = Field(5.0, ge=0.0, le=5.0)
    status: str = "ACTIVE"
    gstin: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class VendorCreate(VendorBase):
    pass


class VendorOut(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
