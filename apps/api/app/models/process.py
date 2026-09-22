from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
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
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ProcessDefinition(Base):
    __tablename__ = "process_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_activities: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class ProcessEvent(Base):
    __tablename__ = "process_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(50), default="employee", nullable=False)
    source_system: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    process_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    activity: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    activity_category: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    object_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class ProcessCase(Base):
    __tablename__ = "process_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    process_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    variant_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    shadow_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class ShadowAlert(Base):
    __tablename__ = "shadow_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    case_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    process_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unapproved_tool: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # Critical, High, Medium, Low
    estimated_leakage: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Shadow score components
    shadow_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    score_band: Mapped[str] = mapped_column(String(50), nullable=False)  # Normal, Process Variation, Suspicious, Strong Shadow Process
    deviation_component: Mapped[float] = mapped_column(Float, nullable=False)
    recurrence_component: Mapped[float] = mapped_column(Float, nullable=False)
    consistency_component: Mapped[float] = mapped_column(Float, nullable=False)
    cross_system_component: Mapped[float] = mapped_column(Float, nullable=False)
    business_risk_component: Mapped[float] = mapped_column(Float, nullable=False)
    
    # ML Score
    ml_anomaly_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="Flagged", index=True, nullable=False)  # Flagged, Investigating, Resolved
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)

    feedbacks: Mapped[List["ShadowFeedback"]] = relationship("ShadowFeedback", back_populates="alert", cascade="all, delete-orphan")


class ShadowFeedback(Base):
    __tablename__ = "shadow_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("shadow_alerts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feedback_label: Mapped[str] = mapped_column(String(50), nullable=False)  # Valid Shadow Process, Normal Variation, False Alert, Needs Investigation
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    alert: Mapped["ShadowAlert"] = relationship("ShadowAlert", back_populates="feedbacks")
    user: Mapped["User"] = relationship("User")
