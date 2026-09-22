from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.identity import User
from app.models.iot import AlertSeverity, AlertStatus, SensorStatus, SensorType
from app.schemas.iot import (
    InfrastructureAlertResponse,
    IngestionResult,
    PhysicalAreaCreate,
    PhysicalAreaResponse,
    PhysicalAreaUpdate,
    ResolveAlertRequest,
    SensorBatchEventsCreate,
    SensorCreate,
    SensorReadingCreate,
    SensorResponse,
    SensorUpdate,
)
from app.services.iot_service import IoTService

router = APIRouter(tags=["Physical Infrastructure & IoT"])


# ─── Physical Areas ────────────────────────────────────────────────────────────

@router.get("/physical/areas", response_model=List[PhysicalAreaResponse])
async def list_areas(
    status: Optional[str] = Query(None, description="Filter by area status (NORMAL, WARNING, CRITICAL)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all physical areas / zones for the organization."""
    return await IoTService.list_areas(
        db=db,
        org_id=current_user.organization_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/physical/areas",
    response_model=PhysicalAreaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_area(
    area_in: PhysicalAreaCreate,
    current_user: User = Depends(require_permission("admin:configure")),
    db: AsyncSession = Depends(get_db),
):
    """Register a new physical area / zone (admin)."""
    return await IoTService.create_area(
        db=db,
        org_id=current_user.organization_id,
        area_in=area_in,
        creator=current_user,
    )


@router.get("/physical/areas/{area_id}", response_model=PhysicalAreaResponse)
async def get_area(
    area_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a single physical area including its sensors and active alerts."""
    area = await IoTService.get_area_by_id(db=db, area_id=area_id, org_id=current_user.organization_id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical area not found")
    return area


# ─── Sensors ──────────────────────────────────────────────────────────────────

@router.get("/physical/sensors", response_model=List[SensorResponse])
async def list_sensors(
    area_id: Optional[int] = None,
    sensor_type: Optional[SensorType] = None,
    sensor_status: Optional[SensorStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_permission("sensor:read")),
    db: AsyncSession = Depends(get_db),
):
    """List all sensors with optional filters by area, type, or status."""
    return await IoTService.list_sensors(
        db=db,
        org_id=current_user.organization_id,
        area_id=area_id,
        sensor_type=sensor_type.value if sensor_type else None,
        status=sensor_status.value if sensor_status else None,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/physical/sensors",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_sensor(
    sensor_in: SensorCreate,
    current_user: User = Depends(require_permission("admin:configure")),
    db: AsyncSession = Depends(get_db),
):
    """Register a new IoT sensor device in an area (admin)."""
    try:
        return await IoTService.create_sensor(
            db=db,
            org_id=current_user.organization_id,
            sensor_in=sensor_in,
            creator=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ─── Sensor Event Ingestion ───────────────────────────────────────────────────

@router.post("/physical/events", response_model=IngestionResult)
async def ingest_sensor_event(
    event_in: SensorReadingCreate,
    current_user: User = Depends(require_permission("sensor:read")),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a single sensor reading.

    Automatically evaluates configured thresholds and generates operational
    alerts when a breach is detected. All state transitions are server-authoritative
    and persisted in the audit trail.
    """
    try:
        reading, alert = await IoTService.ingest_event(
            db=db,
            org_id=current_user.organization_id,
            event_in=event_in,
        )
        alerts = [alert] if alert else []
        return IngestionResult(
            status="SUCCESS",
            readings_processed=1,
            alerts_generated=len(alerts),
            alerts=alerts,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/physical/events/batch", response_model=IngestionResult)
async def ingest_sensor_events_batch(
    batch_in: SensorBatchEventsCreate,
    current_user: User = Depends(require_permission("sensor:read")),
    db: AsyncSession = Depends(get_db),
):
    """Ingest a batch of sensor readings in a single request (e.g., from an IoT gateway)."""
    return await IoTService.ingest_batch_events(
        db=db,
        org_id=current_user.organization_id,
        events=batch_in.events,
    )


# ─── Infrastructure Alerts ────────────────────────────────────────────────────

@router.get("/physical/alerts", response_model=List[InfrastructureAlertResponse])
async def list_infrastructure_alerts(
    alert_status: Optional[AlertStatus] = Query(None, alias="status"),
    severity: Optional[AlertSeverity] = None,
    area_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_permission("sensor:read")),
    db: AsyncSession = Depends(get_db),
):
    """List infrastructure alerts with optional filters by status, severity, or area."""
    return await IoTService.list_alerts(
        db=db,
        org_id=current_user.organization_id,
        status=alert_status.value if alert_status else None,
        severity=severity.value if severity else None,
        area_id=area_id,
        limit=limit,
        offset=offset,
    )


@router.post("/physical/alerts/{alert_id}/acknowledge", response_model=InfrastructureAlertResponse)
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(require_permission("sensor:read")),
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an active infrastructure alert."""
    try:
        return await IoTService.acknowledge_alert(
            db=db,
            alert_id=alert_id,
            org_id=current_user.organization_id,
            user=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/physical/alerts/{alert_id}/resolve", response_model=InfrastructureAlertResponse)
async def resolve_alert(
    alert_id: int,
    resolve_in: ResolveAlertRequest,
    current_user: User = Depends(require_permission("sensor:read")),
    db: AsyncSession = Depends(get_db),
):
    """Mark an infrastructure alert as resolved with optional resolution notes."""
    try:
        return await IoTService.resolve_alert(
            db=db,
            alert_id=alert_id,
            org_id=current_user.organization_id,
            user=current_user,
            resolution_notes=resolve_in.resolution_notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
