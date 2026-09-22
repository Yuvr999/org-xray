import enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
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


class SensorType(str, enum.Enum):
    OCCUPANCY = "OCCUPANCY"
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    POWER = "POWER"
    HEARTBEAT = "HEARTBEAT"


class SensorStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    WARNING = "WARNING"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class AlertSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class AreaStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class PhysicalArea(Base):
    __tablename__ = "physical_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    building: Mapped[str] = mapped_column(String(100), nullable=False)
    floor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    current_occupancy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=AreaStatus.NORMAL.value, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    organization = relationship("Organization")
    sensors: Mapped[List["Sensor"]] = relationship("Sensor", back_populates="area", cascade="all, delete-orphan")
    alerts: Mapped[List["InfrastructureAlert"]] = relationship("InfrastructureAlert", back_populates="area")


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    area_id: Mapped[int] = mapped_column(Integer, ForeignKey("physical_areas.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sensor_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="count")
    status: Mapped[str] = mapped_column(String(50), index=True, default=SensorStatus.ONLINE.value, nullable=False)
    min_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_reading_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_reading_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    organization = relationship("Organization")
    area: Mapped["PhysicalArea"] = relationship("PhysicalArea", back_populates="sensors")
    readings: Mapped[List["SensorReading"]] = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")
    alerts: Mapped[List["InfrastructureAlert"]] = relationship("InfrastructureAlert", back_populates="sensor")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    sensor_id: Mapped[int] = mapped_column(Integer, ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quality: Mapped[str] = mapped_column(String(50), default="GOOD", nullable=False)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="readings")


class InfrastructureAlert(Base):
    __tablename__ = "infrastructure_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    sensor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sensors.id", ondelete="SET NULL"), nullable=True)
    area_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("physical_areas.id", ondelete="SET NULL"), nullable=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default=AlertSeverity.WARNING.value, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    condition_breached: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=AlertStatus.ACTIVE.value, index=True, nullable=False)
    
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization")
    sensor: Mapped[Optional["Sensor"]] = relationship("Sensor", back_populates="alerts")
    area: Mapped[Optional["PhysicalArea"]] = relationship("PhysicalArea", back_populates="alerts")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
