import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class GSTINStatus(str, enum.Enum):
    VALID = "VALID"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_CHECKSUM = "INVALID_CHECKSUM"
    PROVIDER_VERIFIED = "PROVIDER_VERIFIED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_NEGATIVE = "PROVIDER_NEGATIVE"


class GSTINVerificationRecord(Base):
    __tablename__ = "gstin_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    gstin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_format_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_checksum_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_live_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    legal_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    trade_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    state_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    taxpayer_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    provider_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    __table_args__ = (
        Index("ix_gstin_verifications_org_gstin", "organization_id", "gstin"),
    )
