import os
import platform
import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import check_db_health
from app.services.redis import check_redis_health
from app.services.alerting_service import alerting_service, AlertSeverity, AlertEvent

router = APIRouter(prefix="/metrics", tags=["Observability & Metrics"])

# Process start time for uptime calculation
START_TIME = time.time()


class SystemMetricsResponse(BaseModel):
    uptime_seconds: float
    environment: str
    python_version: str
    os_info: str
    dependencies: Dict[str, bool]
    alert_summary: Dict[str, int]


@router.get("", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Returns system telemetry, uptime, dependency health, and operational alert counters.
    """
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    
    alerts = alerting_service.get_recent_alerts(limit=500)
    alert_counts = {
        "INFO": sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
        "WARNING": sum(1 for a in alerts if a.severity == AlertSeverity.WARNING),
        "ERROR": sum(1 for a in alerts if a.severity == AlertSeverity.ERROR),
        "CRITICAL": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
    }

    return SystemMetricsResponse(
        uptime_seconds=round(time.time() - START_TIME, 2),
        environment=settings.ENVIRONMENT,
        python_version=platform.python_version(),
        os_info=f"{platform.system()} {platform.release()}",
        dependencies={
            "database": db_ok,
            "redis": redis_ok,
        },
        alert_summary=alert_counts
    )


@router.get("/alerts", response_model=List[AlertEvent])
async def get_recent_alerts(
    limit: int = Query(50, ge=1, le=200),
    min_severity: str = Query("INFO")
):
    """
    Retrieve operational alerts from the ring buffer.
    """
    try:
        sev = AlertSeverity(min_severity.upper())
    except ValueError:
        sev = AlertSeverity.INFO
    return alerting_service.get_recent_alerts(limit=limit, min_severity=sev)
