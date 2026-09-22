from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Invoice Item Schemas ---

class InvoiceItemBase(BaseModel):
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    taxable_amount: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    line_number: Optional[int] = None


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Invoice Document Schemas ---

class InvoiceDocumentResponse(BaseModel):
    id: int
    invoice_id: int
    original_filename: str
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_hash: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Invoice Extraction Schemas ---

class InvoiceExtractionResponse(BaseModel):
    id: int
    invoice_id: int
    extraction_method: str
    extracted_fields: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Invoice Validation Schemas ---

class InvoiceValidationResponse(BaseModel):
    id: int
    invoice_id: int
    rule_name: str
    severity: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Duplicate Candidate Schemas ---

class DuplicateCandidateResponse(BaseModel):
    id: int
    invoice_id: int
    candidate_invoice_id: int
    match_type: str
    similarity_score: Optional[float] = None
    evidence: Optional[Dict[str, Any]] = None
    created_at: datetime

    # Inline summary of the candidate invoice
    candidate_vendor_name: Optional[str] = None
    candidate_invoice_number: Optional[str] = None
    candidate_grand_total: Optional[float] = None
    candidate_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DuplicateDecisionCreate(BaseModel):
    candidate_id: int = Field(..., description="ID of the duplicate candidate record")
    decision: str = Field(..., description="One of: confirmed_duplicate, not_duplicate, needs_investigation")
    reason: Optional[str] = Field(None, description="Human explanation for the decision")

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        valid = {"confirmed_duplicate", "not_duplicate", "needs_investigation"}
        if v not in valid:
            raise ValueError(f"decision must be one of {valid}")
        return v


class DuplicateDecisionResponse(BaseModel):
    id: int
    invoice_id: int
    candidate_id: int
    decision: str
    decided_by_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Invoice Review Schemas ---

class InvoiceReviewRequest(BaseModel):
    action: str = Field(..., description="One of: verify, reject")
    notes: Optional[str] = Field(None, description="Optional review notes")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        valid = {"verify", "reject"}
        if v not in valid:
            raise ValueError(f"action must be one of {valid}")
        return v


# --- Invoice Response Schemas ---

class InvoiceListItem(BaseModel):
    id: int
    status: str
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    grand_total: Optional[float] = None
    currency: str = "INR"
    extraction_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceDetail(BaseModel):
    id: int
    organization_id: int
    uploaded_by_id: Optional[int] = None
    status: str
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    currency: str = "INR"
    po_reference: Optional[str] = None
    subtotal: Optional[float] = None
    total_tax: Optional[float] = None
    grand_total: Optional[float] = None
    extraction_confidence: Optional[float] = None
    extraction_method: Optional[str] = None
    document_hash: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    items: List[InvoiceItemResponse] = []
    documents: List[InvoiceDocumentResponse] = []
    extractions: List[InvoiceExtractionResponse] = []
    validation_results: List[InvoiceValidationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    items: List[InvoiceListItem]
    total: int
    page: int
    page_size: int
