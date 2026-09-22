from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import User
from app.models.iot import (
    AlertSeverity,
    AlertStatus,
    AreaStatus,
    InfrastructureAlert,
    PhysicalArea,
    Sensor,
    SensorReading,
    SensorStatus,
    SensorType,
)
from app.schemas.iot import (
    IngestionResult,
    PhysicalAreaCreate,
    PhysicalAreaUpdate,
    SensorCreate,
    SensorReadingCreate,
    SensorUpdate,
)
from app.services.audit_service import create_audit_log


def utc_now():
    return datetime.now(timezone.utc)


class IoTService:
    @staticmethod
    async def create_area(
        db: AsyncSession,
        org_id: int,
        area_in: PhysicalAreaCreate,
        creator: Optional[User] = None,
    ) -> PhysicalArea:
        area = PhysicalArea(
            organization_id=org_id,
            name=area_in.name,
            code=area_in.code,
            building=area_in.building,
            floor=area_in.floor,
            capacity=area_in.capacity,
            description=area_in.description,
            current_occupancy=0,
            status=AreaStatus.NORMAL.value,
        )
        db.add(area)
        await db.commit()
        await db.refresh(area)

        if creator:
            await create_audit_log(
                db=db,
                organization_id=org_id,
                user_id=creator.id,
                action="PHYSICAL_AREA_CREATED",
                resource_type="physical_area",
                resource_id=str(area.id),
                new_values={"name": area.name, "code": area.code, "capacity": area.capacity},
            )
        return area

    @staticmethod
    async def list_areas(
        db: AsyncSession,
        org_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PhysicalArea]:
        query = select(PhysicalArea).where(PhysicalArea.organization_id == org_id)
        if status:
            query = query.where(PhysicalArea.status == status)
        query = query.order_by(PhysicalArea.name).limit(limit).offset(offset)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def get_area_by_id(db: AsyncSession, area_id: int, org_id: int) -> Optional[PhysicalArea]:
        query = (
            select(PhysicalArea)
            .where(PhysicalArea.id == area_id, PhysicalArea.organization_id == org_id)
            .options(selectinload(PhysicalArea.sensors), selectinload(PhysicalArea.alerts))
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def create_sensor(
        db: AsyncSession,
        org_id: int,
        sensor_in: SensorCreate,
        creator: Optional[User] = None,
    ) -> Sensor:
        # Validate area exists in org
        area_stmt = select(PhysicalArea).where(
            PhysicalArea.id == sensor_in.area_id,
            PhysicalArea.organization_id == org_id,
        )
        area_res = await db.execute(area_stmt)
        if not area_res.scalar_one_or_none():
            raise ValueError(f"PhysicalArea {sensor_in.area_id} not found in this organization")

        sensor = Sensor(
            organization_id=org_id,
            area_id=sensor_in.area_id,
            device_id=sensor_in.device_id,
            name=sensor_in.name or f"Sensor {sensor_in.device_id}",
            sensor_type=sensor_in.sensor_type.value if hasattr(sensor_in.sensor_type, "value") else str(sensor_in.sensor_type),
            unit=sensor_in.unit,
            status=SensorStatus.ONLINE.value,
            min_threshold=sensor_in.min_threshold,
            max_threshold=sensor_in.max_threshold,
        )
        db.add(sensor)
        await db.commit()
        await db.refresh(sensor)

        if creator:
            await create_audit_log(
                db=db,
                organization_id=org_id,
                user_id=creator.id,
                action="SENSOR_REGISTERED",
                resource_type="sensor",
                resource_id=str(sensor.id),
                new_values={
                    "device_id": sensor.device_id,
                    "sensor_type": sensor.sensor_type,
                    "area_id": sensor.area_id,
                },
            )
        return sensor

    @staticmethod
    async def list_sensors(
        db: AsyncSession,
        org_id: int,
        area_id: Optional[int] = None,
        sensor_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Sensor]:
        query = select(Sensor).where(Sensor.organization_id == org_id)
        if area_id:
            query = query.where(Sensor.area_id == area_id)
        if sensor_type:
            query = query.where(Sensor.sensor_type == sensor_type)
        if status:
            query = query.where(Sensor.status == status)
        query = query.order_by(Sensor.id).limit(limit).offset(offset)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def ingest_event(
        db: AsyncSession,
        org_id: int,
        event_in: SensorReadingCreate,
    ) -> Tuple[SensorReading, Optional[InfrastructureAlert]]:
        # Find sensor by device_id and organization
        stmt = (
            select(Sensor)
            .where(Sensor.device_id == event_in.device_id, Sensor.organization_id == org_id)
            .options(selectinload(Sensor.area))
        )
        res = await db.execute(stmt)
        sensor = res.scalar_one_or_none()
        if not sensor:
            raise ValueError(f"Sensor device '{event_in.device_id}' is not registered in this organization")

        timestamp = event_in.timestamp or utc_now()
        reading = SensorReading(
            organization_id=org_id,
            sensor_id=sensor.id,
            device_id=sensor.device_id,
            timestamp=timestamp,
            metric_type=event_in.metric_type,
            metric_value=event_in.metric_value,
            unit=event_in.unit or sensor.unit,
            quality=event_in.quality or "GOOD",
            raw_payload=event_in.raw_payload,
        )
        db.add(reading)

        # Update sensor last reading
        sensor.last_reading_value = event_in.metric_value
        sensor.last_reading_at = timestamp

        alert = await IoTService._evaluate_thresholds(db, sensor, event_in.metric_value)
        await db.commit()
        await db.refresh(reading)
        if alert:
            await db.refresh(alert)

        return reading, alert

    @staticmethod
    async def ingest_batch_events(
        db: AsyncSession,
        org_id: int,
        events: List[SensorReadingCreate],
    ) -> IngestionResult:
        alerts_generated = []
        readings_count = 0

        for evt in events:
            try:
                _, alert = await IoTService.ingest_event(db, org_id, evt)
                readings_count += 1
                if alert:
                    alerts_generated.append(alert)
            except Exception:
                continue

        return IngestionResult(
            status="SUCCESS",
            readings_processed=readings_count,
            alerts_generated=len(alerts_generated),
            alerts=alerts_generated,
        )

    @staticmethod
    async def _evaluate_thresholds(
        db: AsyncSession,
        sensor: Sensor,
        value: float,
    ) -> Optional[InfrastructureAlert]:
        alert: Optional[InfrastructureAlert] = None
        area = sensor.area

        # 1. Check Max Threshold Breach
        if sensor.max_threshold is not None and value > sensor.max_threshold:
            severity = AlertSeverity.CRITICAL.value if value > (sensor.max_threshold * 1.2) else AlertSeverity.WARNING.value
            sensor.status = SensorStatus.WARNING.value if severity == AlertSeverity.WARNING.value else SensorStatus.MAINTENANCE.value
            
            alert = InfrastructureAlert(
                organization_id=sensor.organization_id,
                sensor_id=sensor.id,
                area_id=sensor.area_id,
                device_id=sensor.device_id,
                alert_type="THRESHOLD_BREACH_MAX",
                severity=severity,
                message=f"High metric alert: {sensor.name or sensor.device_id} reported {value} {sensor.unit} (Threshold: >{sensor.max_threshold})",
                metric_value=value,
                threshold_value=sensor.max_threshold,
                condition_breached=f"Value {value} > Max {sensor.max_threshold}",
                status=AlertStatus.ACTIVE.value,
                triggered_at=utc_now(),
                recommended_action=f"Inspect environmental conditions or cooling in {area.name if area else 'area'}",
            )
            db.add(alert)

        # 2. Check Min Threshold Breach
        elif sensor.min_threshold is not None and value < sensor.min_threshold:
            severity = AlertSeverity.CRITICAL.value if value < (sensor.min_threshold * 0.8) else AlertSeverity.WARNING.value
            sensor.status = SensorStatus.WARNING.value if severity == AlertSeverity.WARNING.value else SensorStatus.MAINTENANCE.value
            
            alert = InfrastructureAlert(
                organization_id=sensor.organization_id,
                sensor_id=sensor.id,
                area_id=sensor.area_id,
                device_id=sensor.device_id,
                alert_type="THRESHOLD_BREACH_MIN",
                severity=severity,
                message=f"Low metric alert: {sensor.name or sensor.device_id} reported {value} {sensor.unit} (Threshold: <{sensor.min_threshold})",
                metric_value=value,
                threshold_value=sensor.min_threshold,
                condition_breached=f"Value {value} < Min {sensor.min_threshold}",
                status=AlertStatus.ACTIVE.value,
                triggered_at=utc_now(),
                recommended_action=f"Check power supply or minimum operating parameters for {sensor.device_id}",
            )
            db.add(alert)
        else:
            # Within threshold bounds
            sensor.status = SensorStatus.ONLINE.value

        # 3. Check Area Occupancy if sensor is OCCUPANCY type
        if sensor.sensor_type == SensorType.OCCUPANCY.value and area:
            area.current_occupancy = int(value)
            if area.current_occupancy > area.capacity:
                area.status = AreaStatus.CRITICAL.value
                occupancy_alert = InfrastructureAlert(
                    organization_id=sensor.organization_id,
                    sensor_id=sensor.id,
                    area_id=area.id,
                    device_id=sensor.device_id,
                    alert_type="OCCUPANCY_EXCEEDED",
                    severity=AlertSeverity.CRITICAL.value,
                    message=f"Overcapacity detected in {area.name}: {area.current_occupancy} persons (Capacity: {area.capacity})",
                    metric_value=value,
                    threshold_value=float(area.capacity),
                    condition_breached=f"Current {area.current_occupancy} > Max {area.capacity}",
                    status=AlertStatus.ACTIVE.value,
                    triggered_at=utc_now(),
                    recommended_action="Enforce safety capacity protocols and re-route personnel",
                )
                db.add(occupancy_alert)
                if not alert:
                    alert = occupancy_alert
            else:
                area.status = AreaStatus.NORMAL.value

        return alert

    @staticmethod
    async def list_alerts(
        db: AsyncSession,
        org_id: int,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        area_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[InfrastructureAlert]:
        query = select(InfrastructureAlert).where(InfrastructureAlert.organization_id == org_id)
        if status:
            query = query.where(InfrastructureAlert.status == status)
        if severity:
            query = query.where(InfrastructureAlert.severity == severity)
        if area_id:
            query = query.where(InfrastructureAlert.area_id == area_id)

        query = query.order_by(desc(InfrastructureAlert.triggered_at)).limit(limit).offset(offset)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        alert_id: int,
        org_id: int,
        user: User,
    ) -> InfrastructureAlert:
        stmt = select(InfrastructureAlert).where(
            InfrastructureAlert.id == alert_id,
            InfrastructureAlert.organization_id == org_id,
        )
        res = await db.execute(stmt)
        alert = res.scalar_one_or_none()
        if not alert:
            raise ValueError("Infrastructure alert not found")

        alert.status = AlertStatus.ACKNOWLEDGED.value
        await db.commit()
        await db.refresh(alert)

        await create_audit_log(
            db=db,
            organization_id=org_id,
            user_id=user.id,
            action="INFRASTRUCTURE_ALERT_ACKNOWLEDGED",
            resource_type="infrastructure_alert",
            resource_id=str(alert.id),
            new_values={"status": alert.status},
        )
        return alert

    @staticmethod
    async def resolve_alert(
        db: AsyncSession,
        alert_id: int,
        org_id: int,
        user: User,
        resolution_notes: Optional[str] = None,
    ) -> InfrastructureAlert:
        stmt = select(InfrastructureAlert).where(
            InfrastructureAlert.id == alert_id,
            InfrastructureAlert.organization_id == org_id,
        )
        res = await db.execute(stmt)
        alert = res.scalar_one_or_none()
        if not alert:
            raise ValueError("Infrastructure alert not found")

        alert.status = AlertStatus.RESOLVED.value
        alert.resolved_at = utc_now()
        alert.resolved_by_id = user.id
        alert.resolution_notes = resolution_notes
        await db.commit()
        await db.refresh(alert)

        await create_audit_log(
            db=db,
            organization_id=org_id,
            user_id=user.id,
            action="INFRASTRUCTURE_ALERT_RESOLVED",
            resource_type="infrastructure_alert",
            resource_id=str(alert.id),
            new_values={"status": alert.status, "resolution_notes": resolution_notes},
        )
        return alert
