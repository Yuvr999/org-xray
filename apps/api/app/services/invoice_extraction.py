"""
Invoice Field Extraction Service

Extracts structured invoice fields from raw PDF text.
Uses regex-based pattern matching as the initial deterministic extraction method.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ExtractedInvoiceFields:
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    total_tax: Optional[float] = None
    grand_total: Optional[float] = None
    po_reference: Optional[str] = None
    currency: str = "INR"
    line_items: Optional[List[Dict[str, Any]]] = None
    confidence: float = 0.0


# Common regex patterns for Indian invoices
GSTIN_PATTERN = re.compile(
    r'\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[A-Z]{1}[A-Z0-9]{1})\b'
)

INVOICE_NUMBER_PATTERNS = [
    re.compile(r'(?:Invoice\s*(?:No\.?|Number|#)\s*:?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Bill\s*(?:No\.?|Number|#)\s*:?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Inv\.?\s*(?:No\.?|#)\s*:?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
]

DATE_PATTERNS = [
    re.compile(r'(?:(?:Invoice|Bill|Inv\.?)\s*Date\s*:?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Date\s*:?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Date\s*:?\s*)(\d{2,4}[\-/\.]\d{1,2}[\-/\.]\d{1,2})', re.IGNORECASE),
]

DUE_DATE_PATTERNS = [
    re.compile(r'(?:Due\s*Date\s*:?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Payment\s*Due\s*:?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
]

AMOUNT_PATTERNS = {
    "grand_total": [
        re.compile(r'(?:Grand\s*Total|Total\s*Amount|Net\s*Payable|Amount\s*Due)\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ],
    "subtotal": [
        re.compile(r'(?:Sub\s*[-]?\s*Total|Taxable\s*(?:Amount|Value))\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ],
    "total_tax": [
        re.compile(r'(?:Total\s*Tax|GST\s*(?:Amount)?|\bTax(?![\s]*Invoice)\s*(?:Amount)?|IGST|CGST\s*\+\s*SGST)\s*:?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ],
}

PO_PATTERNS = [
    re.compile(r'(?:PO\s*(?:No\.?|Number|#|Ref\.?)\s*:?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Purchase\s*Order\s*(?:No\.?|Number|#)\s*:?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
]


def _parse_amount(text: str) -> Optional[float]:
    """Parse an amount string like '1,23,456.78' to a float."""
    try:
        cleaned = text.replace(",", "").strip()
        return round(float(cleaned), 2)
    except (ValueError, TypeError):
        return None


def _find_first_match(text: str, patterns: list) -> Optional[str]:
    """Return the first regex match from a list of patterns."""
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            return m.group(1).strip()
    return None


def extract_fields_from_text(raw_text: str) -> ExtractedInvoiceFields:
    """
    Extract structured invoice fields from raw text content.
    Returns extracted fields with a confidence score.
    """
    fields = ExtractedInvoiceFields()
    field_hits = 0
    total_fields = 8  # Number of key fields we attempt to extract

    # Extract GSTIN
    gstin_matches = GSTIN_PATTERN.findall(raw_text)
    if gstin_matches:
        fields.vendor_gstin = gstin_matches[0]
        field_hits += 1

    # Extract invoice number
    inv_num = _find_first_match(raw_text, INVOICE_NUMBER_PATTERNS)
    if inv_num:
        fields.invoice_number = inv_num
        field_hits += 1

    # Extract invoice date
    inv_date = _find_first_match(raw_text, DATE_PATTERNS)
    if inv_date:
        fields.invoice_date = inv_date
        field_hits += 1

    # Extract due date
    due_date = _find_first_match(raw_text, DUE_DATE_PATTERNS)
    if due_date:
        fields.due_date = due_date
        field_hits += 1

    # Extract amounts
    for amount_key, patterns in AMOUNT_PATTERNS.items():
        match_str = _find_first_match(raw_text, patterns)
        if match_str:
            parsed = _parse_amount(match_str)
            if parsed is not None:
                setattr(fields, amount_key, parsed)
                field_hits += 1

    # Extract PO reference
    po_ref = _find_first_match(raw_text, PO_PATTERNS)
    if po_ref:
        fields.po_reference = po_ref
        field_hits += 1

    # Extract vendor name — heuristic: first line or "Bill To" / "From"
    vendor_patterns = [
        re.compile(r'(?:From|Seller|Supplier|Vendor)\s*:?\s*\n?\s*(.+?)(?:\n|$)', re.IGNORECASE),
    ]
    vendor = _find_first_match(raw_text, vendor_patterns)
    if vendor:
        fields.vendor_name = vendor.strip()
        field_hits += 1

    # Calculate confidence
    fields.confidence = round(field_hits / total_fields, 2) if total_fields > 0 else 0.0

    return fields


def compute_document_hash(content: bytes) -> str:
    """Compute SHA-256 hash of document content for exact dedup."""
    return hashlib.sha256(content).hexdigest()
