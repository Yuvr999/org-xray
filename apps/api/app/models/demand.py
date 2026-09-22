import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class DemandStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CLASSIFIED = "CLASSIFIED"
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RoutingMethod(str, enum.Enum):
    RULE = "rule"
    ML = "ml"
    HUMAN = "human"


class Demand(Base):
    __tablename__ = "demands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    requester_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="General", nullable=False)
    estimated_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    status: Mapped[DemandStatus] = mapped_column(
        Enum(DemandStatus, native_enum=False), default=DemandStatus.DRAFT, nullable=False
    )
    
    routed_department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    routing_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    routing_method: Mapped[Optional[RoutingMethod]] = mapped_column(
        Enum(RoutingMethod, native_enum=False), nullable=True
    )
    routing_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    matched_asset_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization")
    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id])
    department: Mapped[Optional["Department"]] = relationship("Department")
    approvals: Mapped[List["Approval"]] = relationship("Approval", back_populates="demand", cascade="all, delete-orphan", lazy="selectin")


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    demand_id: Mapped[int] = mapped_column(Integer, ForeignKey("demands.id", ondelete="CASCADE"), nullable=False)
    approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, native_enum=False), default=ApprovalStatus.PENDING, nullable=False
    )
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    demand: Mapped["Demand"] = relationship("Demand", back_populates="approvals")
    approver: Mapped[Optional["User"]] = relationship("User")


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(100), index=True, default="National", nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization")
