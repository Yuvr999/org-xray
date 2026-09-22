"""
Invoice Processing Service

Orchestrates the full invoice processing pipeline:
Upload → Store → Extract → Validate → Duplicate Check → Status update

All state transitions are server-side and audited.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import logger
from app.models.invoice import (
    DuplicateMatchType,
    Invoice,
    InvoiceDocument,
    InvoiceDuplicateCandidate,
    InvoiceDuplicateDecision,
    InvoiceExtraction,
    InvoiceItem,
    InvoiceStatus,
    InvoiceValidationResult,
    ValidationSeverity,
)
from app.models.identity import User
from app.services.invoice_extraction import (
    ExtractedInvoiceFields,
    compute_document_hash,
    extract_fields_from_text,
)
from app.services.tax_validation import (
    ValidationResult,
    validate_gst_arithmetic,
    validate_line_item_totals,
)
from app.services.duplicate_detection import (
    DuplicateCandidate,
    find_duplicates,
)
from app.services.storage import get_storage_adapter
from app.services.audit_service import log_audit_event


# --- Valid state transitions ---
VALID_TRANSITIONS = {
    InvoiceStatus.UPLOADED: [InvoiceStatus.PROCESSING],
    InvoiceStatus.PROCESSING: [InvoiceStatus.EXTRACTED, InvoiceStatus.REVIEW_REQUIRED],
    InvoiceStatus.EXTRACTED: [InvoiceStatus.VALIDATED, InvoiceStatus.REVIEW_REQUIRED],
    InvoiceStatus.VALIDATED: [InvoiceStatus.VERIFIED, InvoiceStatus.REVIEW_REQUIRED, InvoiceStatus.REJECTED],
    InvoiceStatus.REVIEW_REQUIRED: [InvoiceStatus.VERIFIED, InvoiceStatus.REJECTED, InvoiceStatus.PROCESSING],
    InvoiceStatus.VERIFIED: [],  # Terminal
    InvoiceStatus.REJECTED: [InvoiceStatus.PROCESSING],  # Can reprocess
}


class InvoiceStateError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


def validate_transition(current: str, target: InvoiceStatus) -> bool:
    """Check if a state transition is valid."""
    try:
        current_status = InvoiceStatus(current)
    except ValueError:
        return False
    allowed = VALID_TRANSITIONS.get(current_status, [])
    return target in allowed


async def transition_status(
    db: AsyncSession,
    invoice: Invoice,
    new_status: InvoiceStatus,
    user: Optional[User] = None,
) -> Invoice:
    """Transition invoice to new status with audit trail."""
    if not validate_transition(invoice.status, new_status):
        raise InvoiceStateError(
            f"Cannot transition from {invoice.status} to {new_status.value}. "
            f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(InvoiceStatus(invoice.status), [])]}"
        )

    old_status = invoice.status
    invoice.status = new_status.value
    invoice.updated_at = datetime.now(timezone.utc)
    db.add(invoice)

    await log_audit_event(
        db=db,
        action="invoice.status_change",
        resource_type="invoice",
        resource_id=str(invoice.id),
        old_values={"status": old_status},
        new_values={"status": new_status.value},
        user=user,
        organization_id=invoice.organization_id,
    )

    return invoice


# --- Upload ---

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/tiff",
}

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


async def upload_invoice(
    db: AsyncSession,
    file_content: bytes,
    filename: str,
    content_type: str,
    user: User,
) -> Invoice:
    """
    Upload an invoice document:
    1. Validate file type and size
    2. Compute document hash
    3. Store file in object storage
    4. Create Invoice and InvoiceDocument records
    5. Set status to UPLOADED
    """
    # Validate content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported file type: {content_type}. "
            f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            f"File size {len(file_content)} bytes exceeds maximum {MAX_FILE_SIZE} bytes"
        )

    # Compute hash
    doc_hash = compute_document_hash(file_content)

    # Store file
    storage = get_storage_adapter()
    stored_path = await storage.save_file(
        file_name=f"invoices/{user.organization_id}/{doc_hash}_{filename}",
        content=file_content,
        content_type=content_type,
    )

    # Create invoice record
    invoice = Invoice(
        organization_id=user.organization_id,
        uploaded_by_id=user.id,
        status=InvoiceStatus.UPLOADED.value,
        document_hash=doc_hash,
    )
    db.add(invoice)
    await db.flush()

    # Create document record
    doc = InvoiceDocument(
        invoice_id=invoice.id,
        original_filename=filename,
        stored_path=stored_path,
        content_type=content_type,
        file_size_bytes=len(file_content),
        file_hash=doc_hash,
    )
    db.add(doc)

    await log_audit_event(
        db=db,
        action="invoice.uploaded",
        resource_type="invoice",
        resource_id=str(invoice.id),
        new_values={
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_content),
            "document_hash": doc_hash,
        },
        user=user,
        organization_id=user.organization_id,
    )

    await db.commit()
    await db.refresh(invoice)

    return invoice


# --- Process Invoice (extraction + validation + dedup) ---

async def process_invoice(
    db: AsyncSession,
    invoice_id: int,
    user: Optional[User] = None,
) -> Invoice:
    """
    Full invoice processing pipeline:
    1. Transition to PROCESSING
    2. Read document content
    3. Extract text (text-layer for PDFs)
    4. Extract structured fields
    5. Run tax validation
    6. Run duplicate detection
    7. Update invoice with extracted data
    8. Set final status
    """
    start_time = time.time()

    # Load invoice with relationships
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id)
        .options(
            selectinload(Invoice.documents),
            selectinload(Invoice.items),
        )
    )
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")

    # Transition to PROCESSING
    await transition_status(db, invoice, InvoiceStatus.PROCESSING, user)

    # Read document content
    raw_text = ""
    if invoice.documents:
        doc = invoice.documents[0]
        storage = get_storage_adapter()
        file_content = await storage.get_file(doc.stored_path)
        if file_content:
            # For now, attempt text-layer extraction (decode as UTF-8)
            # In production, add proper PDF parsing and OCR here
            try:
                raw_text = file_content.decode("utf-8", errors="ignore")
            except Exception:
                raw_text = ""

    processing_time = int((time.time() - start_time) * 1000)

    # Extract fields
    fields = extract_fields_from_text(raw_text)

    # Store extraction record
    extraction = InvoiceExtraction(
        invoice_id=invoice.id,
        extraction_method="text_layer",
        raw_text=raw_text[:10000] if raw_text else None,  # Truncate for storage
        extracted_fields={
            "vendor_name": fields.vendor_name,
            "vendor_gstin": fields.vendor_gstin,
            "invoice_number": fields.invoice_number,
            "invoice_date": fields.invoice_date,
            "due_date": fields.due_date,
            "subtotal": fields.subtotal,
            "total_tax": fields.total_tax,
            "grand_total": fields.grand_total,
            "po_reference": fields.po_reference,
        },
        confidence=fields.confidence,
        model_version="regex_v1",
        processing_time_ms=processing_time,
    )
    db.add(extraction)

    # Update invoice header with extracted fields
    invoice.vendor_name = fields.vendor_name
    invoice.vendor_gstin = fields.vendor_gstin
    invoice.invoice_number = fields.invoice_number
    invoice.subtotal = fields.subtotal
    invoice.total_tax = fields.total_tax
    invoice.grand_total = fields.grand_total
    invoice.po_reference = fields.po_reference
    invoice.extraction_confidence = fields.confidence
    invoice.extraction_method = "text_layer"

    # Parse and set dates
    if fields.invoice_date:
        try:
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    parsed = datetime.strptime(fields.invoice_date, fmt)
                    invoice.invoice_date = parsed.replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    if fields.due_date:
        try:
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    parsed = datetime.strptime(fields.due_date, fmt)
                    invoice.due_date = parsed.replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    # Transition to EXTRACTED
    await transition_status(db, invoice, InvoiceStatus.EXTRACTED, user)

    # --- Tax Validation ---
    validation_results = validate_gst_arithmetic(
        subtotal=fields.subtotal,
        total_tax=fields.total_tax,
        grand_total=fields.grand_total,
        tax_rate=18.0,
    )

    has_errors = False
    for vr in validation_results:
        db_result = InvoiceValidationResult(
            invoice_id=invoice.id,
            rule_name=vr.rule_name,
            severity=vr.severity,
            passed=vr.passed,
            message=vr.message,
            details=vr.details,
        )
        db.add(db_result)
        if not vr.passed and vr.severity == "error":
            has_errors = True

    # --- Duplicate Detection ---
    # Fetch existing invoices in same org for comparison
    existing_stmt = (
        select(Invoice)
        .where(
            Invoice.organization_id == invoice.organization_id,
            Invoice.id != invoice.id,
            Invoice.status.notin_([InvoiceStatus.REJECTED.value]),
        )
    )
    existing_result = await db.execute(existing_stmt)
    existing_invoices = existing_result.scalars().all()

    existing_dicts = [
        {
            "id": inv.id,
            "document_hash": inv.document_hash,
            "vendor_name": inv.vendor_name,
            "vendor_gstin": inv.vendor_gstin,
            "invoice_number": inv.invoice_number,
            "grand_total": float(inv.grand_total) if inv.grand_total else None,
            "invoice_date": inv.invoice_date,
            "status": inv.status,
        }
        for inv in existing_invoices
    ]

    new_dict = {
        "id": invoice.id,
        "document_hash": invoice.document_hash,
        "vendor_name": invoice.vendor_name,
        "vendor_gstin": invoice.vendor_gstin,
        "invoice_number": invoice.invoice_number,
        "grand_total": float(invoice.grand_total) if invoice.grand_total else None,
        "invoice_date": invoice.invoice_date,
        "status": invoice.status,
    }

    dup_candidates = find_duplicates(new_dict, existing_dicts)
    has_duplicates = len(dup_candidates) > 0

    for dc in dup_candidates:
        db_dup = InvoiceDuplicateCandidate(
            invoice_id=invoice.id,
            candidate_invoice_id=dc.candidate_invoice_id,
            match_type=dc.match_type,
            similarity_score=dc.similarity_score,
            evidence=dc.evidence,
        )
        db.add(db_dup)

    # --- Set final status ---
    if has_errors or has_duplicates or (fields.confidence < 0.5):
        await transition_status(db, invoice, InvoiceStatus.REVIEW_REQUIRED, user)
    else:
        await transition_status(db, invoice, InvoiceStatus.VALIDATED, user)

    await db.commit()
    await db.refresh(invoice)

    logger.info(
        f"Invoice {invoice.id} processed: status={invoice.status}, "
        f"confidence={fields.confidence}, duplicates={len(dup_candidates)}, "
        f"validation_errors={has_errors}, processing_time={processing_time}ms"
    )

    return invoice


# --- List invoices ---

async def list_invoices(
    db: AsyncSession,
    organization_id: int,
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    vendor_filter: Optional[str] = None,
) -> Tuple[List[Invoice], int]:
    """List invoices with pagination and optional filters."""
    stmt = select(Invoice).where(Invoice.organization_id == organization_id)

    if status_filter:
        stmt = stmt.where(Invoice.status == status_filter)
    if vendor_filter:
        stmt = stmt.where(Invoice.vendor_name.ilike(f"%{vendor_filter}%"))

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Paginate
    stmt = stmt.order_by(Invoice.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    invoices = list(result.scalars().all())

    return invoices, total


# --- Get invoice detail ---

async def get_invoice_detail(
    db: AsyncSession,
    invoice_id: int,
    organization_id: int,
) -> Optional[Invoice]:
    """Get full invoice detail with all relationships."""
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.organization_id == organization_id)
        .options(
            selectinload(Invoice.items),
            selectinload(Invoice.documents),
            selectinload(Invoice.extractions),
            selectinload(Invoice.validation_results),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# --- Get duplicate candidates ---

async def get_duplicate_candidates(
    db: AsyncSession,
    invoice_id: int,
) -> List[InvoiceDuplicateCandidate]:
    """Get duplicate candidates for an invoice."""
    stmt = (
        select(InvoiceDuplicateCandidate)
        .where(InvoiceDuplicateCandidate.invoice_id == invoice_id)
        .options(selectinload(InvoiceDuplicateCandidate.candidate_invoice))
        .order_by(InvoiceDuplicateCandidate.similarity_score.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# --- Review invoice ---

async def review_invoice(
    db: AsyncSession,
    invoice_id: int,
    organization_id: int,
    action: str,
    notes: Optional[str],
    user: User,
) -> Invoice:
    """Submit a human review decision on an invoice."""
    invoice = await get_invoice_detail(db, invoice_id, organization_id)
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")

    if action == "verify":
        target_status = InvoiceStatus.VERIFIED
    elif action == "reject":
        target_status = InvoiceStatus.REJECTED
    else:
        raise ValueError(f"Invalid review action: {action}")

    invoice.reviewed_by_id = user.id
    invoice.reviewed_at = datetime.now(timezone.utc)
    invoice.review_notes = notes

    await transition_status(db, invoice, target_status, user)
    await db.commit()
    await db.refresh(invoice)

    return invoice


# --- Record duplicate decision ---

async def record_duplicate_decision(
    db: AsyncSession,
    invoice_id: int,
    candidate_id: int,
    decision: str,
    reason: Optional[str],
    user: User,
) -> InvoiceDuplicateDecision:
    """Record a human decision on a duplicate candidate."""
    dd = InvoiceDuplicateDecision(
        invoice_id=invoice_id,
        candidate_id=candidate_id,
        decision=decision,
        decided_by_id=user.id,
        reason=reason,
    )
    db.add(dd)

    await log_audit_event(
        db=db,
        action="invoice.duplicate_decision",
        resource_type="invoice_duplicate",
        resource_id=str(candidate_id),
        new_values={"decision": decision, "reason": reason},
        user=user,
    )

    await db.commit()
    await db.refresh(dd)
    return dd
