from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any
from app.core.config import settings
from app.core.database import check_db_health
from app.services.redis import check_redis_health

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    dependencies: Dict[str, bool]


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version="1.0.0",
        environment=settings.ENVIRONMENT,
    )


@router.get("/ready", response_model=ReadinessResponse, status_code=status.HTTP_200_OK)
async def readiness_check():
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()

    is_ready = db_ok and redis_ok
    status_str = "ready" if is_ready else "degraded"

    return ReadinessResponse(
        status=status_str,
        dependencies={
            "database": db_ok,
            "redis": redis_ok,
        },
    )
