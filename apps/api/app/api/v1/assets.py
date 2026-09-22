from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.asset import AssetCategory, AssetCondition, AssetStatus
from app.models.identity import User
from app.schemas.asset import (
    AssetAssignmentCreate,
    AssetAssignmentResponse,
    AssetCreate,
    AssetDetailResponse,
    AssetReallocationCreate,
    AssetReallocationDecision,
    AssetReallocationResponse,
    AssetResponse,
    AssetReturnCreate,
    AssetReturnResponse,
    AssetUpdate,
    ReuseRecommendationResponse,
)
from app.services.asset_service import AssetService

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=List[AssetResponse])
async def list_assets(
    category: Optional[AssetCategory] = None,
    status: Optional[AssetStatus] = None,
    condition: Optional[AssetCondition] = None,
    department_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all assets for the organization with optional filtering."""
    return await AssetService.list_assets(
        db=db,
        org_id=current_user.organization_id,
        category=category.value if category else None,
        status=status.value if status else None,
        condition=condition.value if condition else None,
        department_id=department_id,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_in: AssetCreate,
    current_user: User = Depends(require_permission("asset:reallocate")),
    db: AsyncSession = Depends(get_db),
):
    """Register a new enterprise asset."""
    return await AssetService.create_asset(
        db=db,
        org_id=current_user.organization_id,
        asset_in=asset_in,
        creator=current_user,
    )


@router.get("/recommendations", response_model=ReuseRecommendationResponse)
async def get_reuse_recommendations(
    demand_id: Optional[int] = Query(None, description="Demand request ID to match assets against"),
    category: Optional[str] = Query(None, description="Category filter (e.g. LAPTOP, SERVER)"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ranked, explainable asset reuse recommendations for procurement demand avoidance."""
    return await AssetService.recommend_assets_for_demand(
        db=db,
        org_id=current_user.organization_id,
        demand_id=demand_id,
        category=category,
        limit=limit,
    )


@router.get("/{asset_id}", response_model=AssetDetailResponse)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single asset by ID along with its assignment and return history."""
    asset = await AssetService.get_asset_by_id(
        db=db,
        asset_id=asset_id,
        org_id=current_user.organization_id,
        load_details=True,
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    update_in: AssetUpdate,
    current_user: User = Depends(require_permission("asset:reallocate")),
    db: AsyncSession = Depends(get_db),
):
    """Update asset metadata or status."""
    asset = await AssetService.get_asset_by_id(
        db=db,
        asset_id=asset_id,
        org_id=current_user.organization_id,
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return await AssetService.update_asset(
        db=db,
        asset=asset,
        update_in=update_in,
        updater=current_user,
    )


@router.post("/{asset_id}/assign", response_model=AssetAssignmentResponse)
async def assign_asset(
    asset_id: int,
    assign_in: AssetAssignmentCreate,
    current_user: User = Depends(require_permission("asset:reallocate")),
    db: AsyncSession = Depends(get_db),
):
    """Assign an available asset to a specific user/department."""
    asset = await AssetService.get_asset_by_id(
        db=db,
        asset_id=asset_id,
        org_id=current_user.organization_id,
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    
    return await AssetService.assign_asset(
        db=db,
        asset=asset,
        user_id=assign_in.user_id,
        assigned_by=current_user,
        department_id=assign_in.department_id,
        demand_id=assign_in.demand_id,
        notes=assign_in.notes,
    )


@router.post("/{asset_id}/return", response_model=AssetReturnResponse)
async def return_asset(
    asset_id: int,
    return_in: AssetReturnCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record an asset return and evaluate its condition for reuse."""
    asset = await AssetService.get_asset_by_id(
        db=db,
        asset_id=asset_id,
        org_id=current_user.organization_id,
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    return await AssetService.return_asset(
        db=db,
        asset=asset,
        returned_by_id=asset.current_assigned_user_id or current_user.id,
        received_by=current_user,
        condition=return_in.condition_on_return.value,
        reason=return_in.reason,
        is_reusable=return_in.is_reusable,
        notes=return_in.notes,
    )


@router.post("/{asset_id}/reallocate", response_model=AssetReallocationResponse)
async def propose_reallocation(
    asset_id: int,
    reallocate_in: AssetReallocationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Propose an available/returned asset reallocation to fulfill an existing demand request."""
    try:
        return await AssetService.propose_reallocation(
            db=db,
            org_id=current_user.organization_id,
            asset_id=asset_id,
            demand_id=reallocate_in.demand_id,
            requester=current_user,
            source_type=reallocate_in.source_type,
            notes=reallocate_in.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reallocations/{reallocation_id}/decide", response_model=AssetReallocationResponse)
async def decide_reallocation(
    reallocation_id: int,
    decision_in: AssetReallocationDecision,
    current_user: User = Depends(require_permission("asset:reallocate")),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject an asset reallocation proposal (manager/admin governance action)."""
    try:
        return await AssetService.decide_reallocation(
            db=db,
            org_id=current_user.organization_id,
            reallocation_id=reallocation_id,
            decider=current_user,
            decision=decision_in.decision,
            notes=decision_in.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
