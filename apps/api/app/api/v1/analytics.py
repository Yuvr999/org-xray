from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import RequirePermission, User
from app.schemas.analytics import (
    AuditSummaryAnalytics,
    ModelPerformanceAnalytics,
    OverviewAnalytics,
    ProcessAnalytics,
    ProcurementAnalytics,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=OverviewAnalytics)
async def get_overview_analytics(
    window: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("audit:read")),
):
    return await AnalyticsService.get_overview(db, current_user.organization_id, window)


@router.get("/procurement", response_model=ProcurementAnalytics)
async def get_procurement_analytics(
    window: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("audit:read")),
):
    return await AnalyticsService.get_procurement(db, current_user.organization_id, window)


@router.get("/processes", response_model=ProcessAnalytics)
async def get_process_analytics(
    window: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("audit:read")),
):
    return await AnalyticsService.get_processes(db, current_user.organization_id, window)


@router.get("/model-performance", response_model=ModelPerformanceAnalytics)
async def get_model_performance_analytics(
    window: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("audit:read")),
):
    return await AnalyticsService.get_model_performance(db, current_user.organization_id, window)


@router.get("/audit-summary", response_model=AuditSummaryAnalytics)
async def get_audit_summary_analytics(
    window: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("audit:read")),
):
    return await AnalyticsService.get_audit_summary(db, current_user.organization_id, window)
