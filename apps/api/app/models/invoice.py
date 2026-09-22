import enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


# --- Invoice Status Enum ---

class InvoiceStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    VALIDATED = "VALIDATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ExtractionMethod(str, enum.Enum):
    TEXT_LAYER = "text_layer"
    OCR = "ocr"
    MANUAL = "manual"


class DuplicateMatchType(str, enum.Enum):
    EXACT_HASH = "exact_hash"
    EXACT_VENDOR_INVOICE = "exact_vendor_invoice"
    NORMALIZED_GSTIN_INVOICE = "normalized_gstin_invoice"
    AMOUNT_DATE_WINDOW = "amount_date_window"
    FUZZY_SIMILARITY = "fuzzy_similarity"


class DuplicateDecisionAction(str, enum.Enum):
    CONFIRMED_DUPLICATE = "confirmed_duplicate"
    NOT_DUPLICATE = "not_duplicate"
    NEEDS_INVESTIGATION = "needs_investigation"


class ValidationSeverity(str, enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# --- Invoice ---

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(30), default=InvoiceStatus.UPLOADED.value, nullable=False, index=True
    )

    # Extracted / entered header fields
    vendor_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    vendor_gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    invoice_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    po_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Amounts
    subtotal: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    total_tax: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    grand_total: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)

    # Extraction metadata
    extraction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Document hash for exact dedup
    document_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    # Review
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    documents: Mapped[List["InvoiceDocument"]] = relationship("InvoiceDocument", back_populates="invoice", cascade="all, delete-orphan")
    extractions: Mapped[List["InvoiceExtraction"]] = relationship("InvoiceExtraction", back_populates="invoice", cascade="all, delete-orphan")
    validation_results: Mapped[List["InvoiceValidationResult"]] = relationship("InvoiceValidationResult", back_populates="invoice", cascade="all, delete-orphan")
    duplicate_candidates: Mapped[List["InvoiceDuplicateCandidate"]] = relationship(
        "InvoiceDuplicateCandidate",
        foreign_keys="InvoiceDuplicateCandidate.invoice_id",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    duplicate_decisions: Mapped[List["InvoiceDuplicateDecision"]] = relationship("InvoiceDuplicateDecision", back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_invoices_org_status", "organization_id", "status"),
        Index("ix_invoices_vendor_gstin_number", "vendor_gstin", "invoice_number"),
    )


# --- Invoice Item ---

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hsn_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    quantity: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    unit_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    taxable_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    tax_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tax_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")


# --- Invoice Document (file references) ---

class InvoiceDocument(Base):
    __tablename__ = "invoice_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="documents")


# --- Invoice Extraction ---

class InvoiceExtraction(Base):
    __tablename__ = "invoice_extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    extraction_method: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_fields: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="extractions")


# --- Invoice Validation Result ---

class InvoiceValidationResult(Base):
    __tablename__ = "invoice_validation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default=ValidationSeverity.INFO.value, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="validation_results")


# --- Invoice Duplicate Candidate ---

class InvoiceDuplicateCandidate(Base):
    __tablename__ = "invoice_duplicate_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    match_type: Mapped[str] = mapped_column(String(50), nullable=False)
    similarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", foreign_keys=[invoice_id], back_populates="duplicate_candidates")
    candidate_invoice: Mapped["Invoice"] = relationship("Invoice", foreign_keys=[candidate_invoice_id])

    __table_args__ = (
        Index("ix_dup_candidates_pair", "invoice_id", "candidate_invoice_id", unique=True),
    )


# --- Invoice Duplicate Decision ---

class InvoiceDuplicateDecision(Base):
    __tablename__ = "invoice_duplicate_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoice_duplicate_candidates.id", ondelete="CASCADE"), nullable=False)

    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    decided_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="duplicate_decisions")
