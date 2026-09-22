from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.identity import User
from app.schemas.vendor import VendorOut, VendorCreate
from app.services.vendor_service import VendorService

router = APIRouter()


@router.get("", response_model=List[VendorOut])
async def list_vendors(
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search and filter approved vendors catalog.
    """
    return await VendorService.list_vendors(
        db,
        organization_id=current_user.organization_id,
        category=category,
        region=region,
    )


@router.get("/{vendor_id}", response_model=VendorOut)
async def get_vendor(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get vendor details by ID.
    """
    vendor = await VendorService.get_vendor_by_id(db, vendor_id, current_user.organization_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.post("", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_in: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("admin:configure")),
):
    """
    Add a new approved vendor to catalog (Admin).
    """
    return await VendorService.create_vendor(db, current_user.organization_id, vendor_in)
