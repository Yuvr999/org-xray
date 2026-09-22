from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RequirePermission, get_current_user
from app.models.identity import User
from app.models.invoice import InvoiceStatus
from app.schemas.invoice import (
    DuplicateCandidateResponse,
    DuplicateDecisionCreate,
    DuplicateDecisionResponse,
    InvoiceDetail,
    InvoiceListResponse,
    InvoiceReviewRequest,
)
from app.services import invoice_service

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post(
    "",
    response_model=InvoiceDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest an invoice",
)
async def upload_invoice(
    file: UploadFile = File(...),
    auto_process: bool = Query(True, description="Immediately run extraction and validation"),
    current_user: User = Depends(RequirePermission("invoice:submit")),
    db: AsyncSession = Depends(get_db),
):
    try:
        content = await file.read()
        invoice = await invoice_service.upload_invoice(
            db=db,
            file_content=content,
            filename=file.filename or "uploaded_invoice",
            content_type=file.content_type or "application/pdf",
            user=current_user,
        )

        if auto_process:
            invoice = await invoice_service.process_invoice(
                db=db,
                invoice_id=invoice.id,
                user=current_user,
            )

        detailed_invoice = await invoice_service.get_invoice_detail(
            db=db,
            invoice_id=invoice.id,
            organization_id=current_user.organization_id,
        )
        return detailed_invoice
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process invoice upload: {str(e)}",
        )


@router.get(
    "",
    response_model=InvoiceListResponse,
    summary="List organization invoices",
)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    vendor: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    invoices, total = await invoice_service.list_invoices(
        db=db,
        organization_id=current_user.organization_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        vendor_filter=vendor,
    )
    return InvoiceListResponse(
        items=invoices,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceDetail,
    summary="Get invoice details with extractions and validations",
)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    invoice = await invoice_service.get_invoice_detail(
        db=db,
        invoice_id=invoice_id,
        organization_id=current_user.organization_id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice #{invoice_id} not found",
        )
    return invoice


@router.post(
    "/{invoice_id}/reprocess",
    response_model=InvoiceDetail,
    summary="Reprocess invoice extraction and validation",
)
async def reprocess_invoice(
    invoice_id: int,
    current_user: User = Depends(RequirePermission("invoice:submit")),
    db: AsyncSession = Depends(get_db),
):
    invoice = await invoice_service.get_invoice_detail(
        db=db,
        invoice_id=invoice_id,
        organization_id=current_user.organization_id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice #{invoice_id} not found",
        )

    try:
        updated = await invoice_service.process_invoice(
            db=db,
            invoice_id=invoice_id,
            user=current_user,
        )
        detailed_invoice = await invoice_service.get_invoice_detail(
            db=db,
            invoice_id=updated.id,
            organization_id=current_user.organization_id,
        )
        return detailed_invoice
    except invoice_service.InvoiceStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reprocessing failed: {str(e)}",
        )


@router.post(
    "/{invoice_id}/review",
    response_model=InvoiceDetail,
    summary="Submit human verification or rejection review",
)
async def review_invoice(
    invoice_id: int,
    review: InvoiceReviewRequest,
    current_user: User = Depends(RequirePermission("invoice:approve")),
    db: AsyncSession = Depends(get_db),
):
    try:
        updated = await invoice_service.review_invoice(
            db=db,
            invoice_id=invoice_id,
            organization_id=current_user.organization_id,
            action=review.action,
            notes=review.notes,
            user=current_user,
        )
        return updated
    except invoice_service.InvoiceStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{invoice_id}/duplicates",
    response_model=List[DuplicateCandidateResponse],
    summary="List duplicate candidates for an invoice",
)
async def get_invoice_duplicates(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    invoice = await invoice_service.get_invoice_detail(
        db=db,
        invoice_id=invoice_id,
        organization_id=current_user.organization_id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice #{invoice_id} not found",
        )

    candidates = await invoice_service.get_duplicate_candidates(db=db, invoice_id=invoice_id)
    results = []
    for c in candidates:
        cand_resp = DuplicateCandidateResponse(
            id=c.id,
            invoice_id=c.invoice_id,
            candidate_invoice_id=c.candidate_invoice_id,
            match_type=c.match_type,
            similarity_score=c.similarity_score,
            evidence=c.evidence,
            created_at=c.created_at,
            candidate_vendor_name=c.candidate_invoice.vendor_name if c.candidate_invoice else None,
            candidate_invoice_number=c.candidate_invoice.invoice_number if c.candidate_invoice else None,
            candidate_grand_total=float(c.candidate_invoice.grand_total) if c.candidate_invoice and c.candidate_invoice.grand_total else None,
            candidate_status=c.candidate_invoice.status if c.candidate_invoice else None,
        )
        results.append(cand_resp)
    return results


@router.post(
    "/{invoice_id}/duplicate-decision",
    response_model=DuplicateDecisionResponse,
    summary="Record human resolution decision on a duplicate candidate",
)
async def record_duplicate_decision(
    invoice_id: int,
    decision_req: DuplicateDecisionCreate,
    current_user: User = Depends(RequirePermission("invoice:approve")),
    db: AsyncSession = Depends(get_db),
):
    try:
        decision = await invoice_service.record_duplicate_decision(
            db=db,
            invoice_id=invoice_id,
            candidate_id=decision_req.candidate_id,
            decision=decision_req.decision,
            reason=decision_req.reason,
            user=current_user,
        )
        return decision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to record duplicate decision: {str(e)}",
        )
