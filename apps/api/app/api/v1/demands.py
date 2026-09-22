from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.identity import User
from app.models.demand import DemandStatus
from app.schemas.demand import (
    DemandCreate,
    DemandOut,
    ClassificationResult,
    ApprovalDecision,
)
from app.services.demand_service import DemandService

router = APIRouter()


@router.post("", response_model=DemandOut, status_code=status.HTTP_201_CREATED)
async def create_demand(
    demand_in: DemandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("demand:create")),
):
    """
    Create a new purchase demand ticket.
    """
    return await DemandService.create_demand(db, current_user, demand_in)


@router.get("", response_model=List[DemandOut])
async def list_demands(
    status_filter: Optional[DemandStatus] = Query(None, alias="status"),
    department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List demands for current user's organization.
    Regular employees see their own demands; managers/admins see organization demands.
    """
    user_id_filter = current_user.id if current_user.primary_role == "employee" else None
    return await DemandService.list_demands(
        db,
        organization_id=current_user.organization_id,
        user_id=user_id_filter,
        department_id=department_id,
        status=status_filter,
    )


@router.get("/{demand_id}", response_model=DemandOut)
async def get_demand(
    demand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed demand ticket info including approvals.
    """
    demand = await DemandService.get_demand_by_id(db, demand_id, current_user.organization_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demand not found")
    return demand


@router.post("/{demand_id}/classify", response_model=DemandOut)
async def classify_demand(
    demand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("demand:create")),
):
    """
    Run demand through the classification pipeline (Rule + ML scaffold).
    """
    return await DemandService.classify_demand(db, current_user, demand_id)


@router.post("/{demand_id}/submit", response_model=DemandOut)
async def submit_demand(
    demand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("demand:create")),
):
    """
    Submit demand ticket for manager approval.
    Validates purchase limits against department budget.
    """
    return await DemandService.submit_demand(db, current_user, demand_id)


@router.post("/{demand_id}/approve", response_model=DemandOut)
async def approve_demand(
    demand_id: int,
    decision: Optional[ApprovalDecision] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("purchase:approve")),
):
    """
    Approve a pending purchase demand ticket (Manager / Admin).
    """
    comments = decision.comments if decision else None
    return await DemandService.approve_demand(db, current_user, demand_id, comments)


@router.post("/{demand_id}/reject", response_model=DemandOut)
async def reject_demand(
    demand_id: int,
    decision: Optional[ApprovalDecision] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("purchase:approve")),
):
    """
    Reject a pending purchase demand ticket (Manager / Admin).
    """
    comments = decision.comments if decision else None
    return await DemandService.reject_demand(db, current_user, demand_id, comments)
