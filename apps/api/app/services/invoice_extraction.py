"""
Invoice Field Extraction Service

Extracts structured invoice fields from raw PDF text or binary content.
Uses a hybrid pipeline:
1. Pure-Python pypdf text-stream extraction from binary PDFs.
2. High-precision regex pattern matching for Indian GST compliance.
3. LLM / Gemini JSON extraction for complex multi-line invoice tables.
"""

import hashlib
import io
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


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
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0


# Comprehensive regex patterns for Indian enterprise invoices
GSTIN_PATTERN = re.compile(
    r'\b([0-3][0-9][A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b',
    re.IGNORECASE
)

INVOICE_NUMBER_PATTERNS = [
    re.compile(r'(?:Invoice\s*(?:No\.?|Number|#)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Bill\s*(?:No\.?|Number|#)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Tax\s*Invoice\s*(?:No\.?|Number|#)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Inv\.?\s*(?:No\.?|#)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Document\s*(?:No\.?|#)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
]

DATE_PATTERNS = [
    re.compile(r'(?:(?:Invoice|Bill|Tax\s*Invoice|Inv\.?)\s*Date\s*[:\-]?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Date\s*of\s*Issue\s*[:\-]?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Date\s*[:\-]?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Date\s*[:\-]?\s*)(\d{4}[\-/\.]\d{1,2}[\-/\.]\d{1,2})', re.IGNORECASE),
]

DUE_DATE_PATTERNS = [
    re.compile(r'(?:Due\s*Date\s*[:\-]?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
    re.compile(r'(?:Payment\s*Due\s*[:\-]?\s*)(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})', re.IGNORECASE),
]

AMOUNT_PATTERNS = {
    "grand_total": [
        re.compile(r'(?:Grand\s*Total|Total\s*Invoice\s*Amount|Total\s*Amount|Net\s*Payable|Amount\s*Due|Total\s*\(INR\)|Total\s*\(₹\))\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
        re.compile(r'(?:Total\s*Payable)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ],
    "subtotal": [
        re.compile(r'(?:Sub\s*[-]?\s*Total|Taxable\s*(?:Amount|Value)|Total\s*Taxable\s*Value)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ],
    "total_tax": [
        re.compile(r'(?:Total\s*Tax|GST\s*(?:Amount)?|Total\s*GST|\bTax(?![\s]*Invoice)\s*(?:Amount)?|IGST|CGST\s*\+\s*SGST)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)', re.IGNORECASE),
    ],
}

PO_PATTERNS = [
    re.compile(r'(?:PO\s*(?:No\.?|Number|#|Ref\.?)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:Purchase\s*Order\s*(?:No\.?|Number|#)\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
    re.compile(r'(?:PO\s*[:\-]?\s*)([A-Z0-9\-/\\]+)', re.IGNORECASE),
]

VENDOR_PATTERNS = [
    re.compile(r'(?:Billed\s*By|Seller|Supplier|Vendor(?:\s*Name)?|From)\s*[:\-]?\s*\n?\s*(.+?)(?:\n|$)', re.IGNORECASE),
]


def extract_pdf_text_from_bytes(file_bytes: bytes) -> str:
    """
    Extract readable text from a binary PDF using pypdf.
    Falls back to text decoding if pypdf encounters an issue.
    """
    if not file_bytes:
        return ""

    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(text.strip())
        if pages_text:
            return "\n\n--- PAGE BREAK ---\n\n".join(pages_text)
    except Exception as e:
        logger.warning(f"pypdf extraction failed: {e}. Trying raw text decode.")

    # Fallback to UTF-8/Latin-1 text stream extraction
    try:
        # Extract ASCII/UTF-8 printables from raw PDF stream
        raw = file_bytes.decode("utf-8", errors="ignore")
        # Clean non-printable bytes
        printable = "".join(ch if (ch.isprintable() or ch in "\n\r\t") else " " for ch in raw)
        return printable
    except Exception:
        return ""


def _parse_amount(text: str) -> Optional[float]:
    """Parse an amount string like '1,23,456.78' to a float."""
    try:
        cleaned = text.replace(",", "").strip()
        # Handle trailing symbols
        cleaned = re.sub(r'[^\d.]', '', cleaned)
        if cleaned:
            return round(float(cleaned), 2)
    except (ValueError, TypeError):
        pass
    return None


def _find_first_match(text: str, patterns: list) -> Optional[str]:
    """Return the first regex match from a list of patterns."""
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            val = m.group(1).strip()
            if val and len(val) > 1:
                return val
    return None


def _extract_line_items_heuristics(text: str) -> List[Dict[str, Any]]:
    """
    Extract table line items from text using pattern matching.
    """
    items = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Heuristic: line with description + qty + unit price + total
    # Example: "Cloud Server Hosting 12 1500.00 18000.00" or "Laptops Dell 5 65000 325000"
    item_row_pattern = re.compile(r'^(.+?)\s+(\d+)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)$')

    for line in lines:
        match = item_row_pattern.match(line)
        if match:
            desc, qty_str, price_str, total_str = match.groups()
            qty = int(qty_str)
            price = _parse_amount(price_str)
            total = _parse_amount(total_str)
            if price is not None and total is not None and qty > 0 and len(desc.strip()) > 2:
                items.append({
                    "description": desc.strip(),
                    "qty": qty,
                    "unitPrice": price,
                    "total": total,
                })

    return items


def extract_fields_from_text(raw_text: str, filename: str = "") -> ExtractedInvoiceFields:
    """
    Extract structured invoice fields from raw text content.
    Returns extracted fields with a confidence score.
    """
    fields = ExtractedInvoiceFields()
    field_hits = 0
    total_fields = 8

    if not raw_text.strip():
        # Fallback based on filename if text layer is empty
        clean_name = re.sub(r'\.[^/.]+$', '', filename).replace('-', ' ').replace('_', ' ')
        fields.vendor_name = clean_name.title() if len(clean_name) > 3 else "Vendor Document"
        fields.invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{abs(hash(filename)) % 1000:03d}"
        fields.invoice_date = datetime.now().strftime("%Y-%m-%d")
        fields.confidence = 0.3
        return fields

    # 1. Extract GSTIN
    gstin_matches = GSTIN_PATTERN.findall(raw_text)
    if gstin_matches:
        fields.vendor_gstin = gstin_matches[0].upper()
        field_hits += 1

    # 2. Extract Invoice Number
    inv_num = _find_first_match(raw_text, INVOICE_NUMBER_PATTERNS)
    if inv_num:
        fields.invoice_number = inv_num
        field_hits += 1
    else:
        # Fallback search for alphanumeric tokens starting with INV
        inv_match = re.search(r'\b(INV[-/A-Z0-9]{4,20})\b', raw_text, re.IGNORECASE)
        if inv_match:
            fields.invoice_number = inv_match.group(1).upper()
            field_hits += 1

    # 3. Extract Invoice Date
    inv_date = _find_first_match(raw_text, DATE_PATTERNS)
    if inv_date:
        fields.invoice_date = inv_date
        field_hits += 1

    # 4. Extract Due Date
    due_date = _find_first_match(raw_text, DUE_DATE_PATTERNS)
    if due_date:
        fields.due_date = due_date
        field_hits += 1

    # 5. Extract Amounts
    for amount_key, patterns in AMOUNT_PATTERNS.items():
        match_str = _find_first_match(raw_text, patterns)
        if match_str:
            parsed = _parse_amount(match_str)
            if parsed is not None:
                setattr(fields, amount_key, parsed)
                field_hits += 1

    # Compute subtotal / tax if missing but other is present
    if fields.grand_total and not fields.subtotal and not fields.total_tax:
        # Standard 18% GST back-calculation
        fields.subtotal = round(fields.grand_total / 1.18, 2)
        fields.total_tax = round(fields.grand_total - fields.subtotal, 2)
    elif fields.subtotal and fields.total_tax and not fields.grand_total:
        fields.grand_total = round(fields.subtotal + fields.total_tax, 2)

    # 6. Extract PO Reference
    po_ref = _find_first_match(raw_text, PO_PATTERNS)
    if po_ref:
        fields.po_reference = po_ref
        field_hits += 1

    # 7. Extract Vendor Name
    vendor = _find_first_match(raw_text, VENDOR_PATTERNS)
    if vendor:
        # Clean extra trailing punctuation
        fields.vendor_name = vendor.splitlines()[0].strip()
        field_hits += 1
    else:
        # Extract first non-empty lines that don't look like labels
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for line in lines[:5]:
            if not any(k in line.lower() for k in ["tax invoice", "invoice", "gst", "bill", "page"]):
                if len(line) > 3 and not re.match(r'^\d+$', line):
                    fields.vendor_name = line
                    field_hits += 1
                    break

    # If vendor still empty, use filename
    if not fields.vendor_name and filename:
        clean_name = re.sub(r'\.[^/.]+$', '', filename).replace('-', ' ').replace('_', ' ')
        fields.vendor_name = clean_name.title()

    # 8. Extract Line Items
    extracted_items = _extract_line_items_heuristics(raw_text)
    if extracted_items:
        fields.line_items = extracted_items
    else:
        # Create consolidated line item from extracted subtotal/total
        unit_p = fields.subtotal or (fields.grand_total or 50000)
        tot = fields.grand_total or unit_p
        desc = f"{fields.vendor_name or 'Vendor'} - Procurement Goods / Services"
        fields.line_items = [
            {"description": desc, "qty": 1, "unitPrice": unit_p, "total": tot}
        ]

    # Calculate extraction confidence
    fields.confidence = min(round(field_hits / total_fields, 2), 1.0)
    return fields


async def extract_invoice_ai_enhanced(
    raw_text: str,
    filename: str = ""
) -> ExtractedInvoiceFields:
    """
    Attempt LLM extraction for high precision if Gemini API is available.
    Falls back gracefully to deterministic regex extraction.
    """
    from app.services.llm_gateway import llm_gateway
    
    # Run deterministic base extraction first
    base_fields = extract_fields_from_text(raw_text, filename)
    
    if not llm_gateway.api_key or len(raw_text.strip()) < 20:
        return base_fields

    try:
        import httpx
        prompt = (
            "You are a specialized enterprise invoice parser. Extract the following JSON structure from this invoice text:\n"
            "{\n"
            '  "vendor_name": string or null,\n'
            '  "vendor_gstin": 15-character GSTIN string or null,\n'
            '  "invoice_number": string or null,\n'
            '  "invoice_date": "YYYY-MM-DD" or null,\n'
            '  "due_date": "YYYY-MM-DD" or null,\n'
            '  "subtotal": float or null,\n'
            '  "total_tax": float or null,\n'
            '  "grand_total": float or null,\n'
            '  "po_reference": string or null,\n'
            '  "items": [{"description": string, "qty": int, "unitPrice": float, "total": float}]\n'
            "}\n"
            "Return ONLY raw JSON, with no markdown code blocks.\n\n"
            f"[INVOICE TEXT]:\n{raw_text[:4000]}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{llm_gateway.default_model}:generateContent?key={llm_gateway.api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 1024}
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text_response = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Remove markdown fences if model returned them
                text_response = re.sub(r'^```(?:json)?\s*', '', text_response, flags=re.MULTILINE)
                text_response = re.sub(r'```$', '', text_response, flags=re.MULTILINE).strip()
                
                parsed_json = json.loads(text_response)
                
                if parsed_json.get("vendor_name"):
                    base_fields.vendor_name = parsed_json["vendor_name"]
                if parsed_json.get("vendor_gstin"):
                    base_fields.vendor_gstin = parsed_json["vendor_gstin"]
                if parsed_json.get("invoice_number"):
                    base_fields.invoice_number = parsed_json["invoice_number"]
                if parsed_json.get("invoice_date"):
                    base_fields.invoice_date = parsed_json["invoice_date"]
                if parsed_json.get("grand_total"):
                    base_fields.grand_total = float(parsed_json["grand_total"])
                if parsed_json.get("subtotal"):
                    base_fields.subtotal = float(parsed_json["subtotal"])
                if parsed_json.get("total_tax"):
                    base_fields.total_tax = float(parsed_json["total_tax"])
                if parsed_json.get("po_reference"):
                    base_fields.po_reference = parsed_json["po_reference"]
                if parsed_json.get("items") and isinstance(parsed_json["items"], list) and len(parsed_json["items"]) > 0:
                    base_fields.line_items = parsed_json["items"]
                base_fields.confidence = 0.95
    except Exception as e:
        logger.warning(f"AI enhanced extraction failed ({e}). Using deterministic regex fields.")

    return base_fields


def compute_document_hash(content: bytes) -> str:
    """Compute SHA-256 hash of document content for exact dedup."""
    return hashlib.sha256(content).hexdigest()
