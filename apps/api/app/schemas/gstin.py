from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GSTINVerifyRequest(BaseModel):
    gstin: str = Field(..., description="15-character GSTIN string to verify")
    skip_live_check: bool = Field(False, description="Set to true to perform structural MOD-36 check only")

    @field_validator("gstin")
    @classmethod
    def validate_gstin_str(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("GSTIN string cannot be empty")
        return v.strip().upper()


class GSTINVerifyResponse(BaseModel):
    id: int
    gstin: str
    is_format_valid: bool
    is_checksum_valid: bool
    is_live_verified: bool
    status: str
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    state_code: Optional[str] = None
    taxpayer_type: Optional[str] = None
    provider_name: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
