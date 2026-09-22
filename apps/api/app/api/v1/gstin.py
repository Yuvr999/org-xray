from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.identity import User
from app.schemas.gstin import GSTINVerifyRequest, GSTINVerifyResponse
from app.services import gstin_service

router = APIRouter(prefix="/gstin", tags=["GSTIN Verification"])


@router.post(
    "/verify",
    response_model=GSTINVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify GSTIN format, MOD-36 checksum, and live provider status",
)
async def verify_gstin(
    req: GSTINVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Perform MOD-36 structural validation and live GSTIN lookup.
    """
    try:
        record = await gstin_service.verify_gstin(
            db=db,
            gstin=req.gstin,
            user=current_user,
            skip_live_check=req.skip_live_check,
        )
        return record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GSTIN verification failed: {str(e)}",
        )


@router.get(
    "/{gstin}",
    response_model=GSTINVerifyResponse,
    summary="Get cached GSTIN verification record",
)
async def get_gstin(
    gstin: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve most recent verification provenance for a given GSTIN.
    """
    record = await gstin_service.get_gstin_verification_history(
        db=db,
        organization_id=current_user.organization_id,
        gstin=gstin,
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification record found for GSTIN '{gstin}'",
        )
    return record
