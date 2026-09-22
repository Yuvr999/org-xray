"""
Invoice Duplicate Detection Engine

Implements the cascade detection strategy from the build plan:
1. Document hash / exact file match
2. Exact vendor + invoice number
3. Normalized vendor GSTIN + invoice number
4. GSTIN + amount + date-window candidate search
5. Fuzzy field similarity

Returns candidate matches with evidence.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from difflib import SequenceMatcher


@dataclass
class DuplicateCandidate:
    candidate_invoice_id: int
    match_type: str
    similarity_score: float
    evidence: Dict[str, Any]


def normalize_gstin(gstin: Optional[str]) -> Optional[str]:
    """Normalize a GSTIN for comparison."""
    if not gstin:
        return None
    return re.sub(r"[^A-Z0-9]", "", gstin.upper().strip())


def normalize_invoice_number(number: Optional[str]) -> Optional[str]:
    """Normalize invoice number for comparison."""
    if not number:
        return None
    # Strip whitespace, standardize separators
    normalized = number.strip().upper()
    normalized = re.sub(r"[\s\-_/\\]+", "", normalized)
    return normalized


def string_similarity(a: Optional[str], b: Optional[str]) -> float:
    """Calculate similarity between two strings using SequenceMatcher."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates(
    new_invoice: dict,
    existing_invoices: List[dict],
    date_window_days: int = 30,
    fuzzy_threshold: float = 0.85,
) -> List[DuplicateCandidate]:
    """
    Run the full duplicate detection cascade against existing invoices.

    new_invoice dict should contain:
        - id, document_hash, vendor_name, vendor_gstin, invoice_number,
          grand_total, invoice_date, status

    existing_invoices list of dicts with same keys.
    """
    candidates: List[DuplicateCandidate] = []
    seen_ids = set()

    new_hash = new_invoice.get("document_hash")
    new_gstin = normalize_gstin(new_invoice.get("vendor_gstin"))
    new_inv_num = normalize_invoice_number(new_invoice.get("invoice_number"))
    new_vendor = new_invoice.get("vendor_name", "")
    new_total = new_invoice.get("grand_total")
    new_date = new_invoice.get("invoice_date")

    for existing in existing_invoices:
        ex_id = existing["id"]
        if ex_id == new_invoice.get("id"):
            continue
        if ex_id in seen_ids:
            continue

        # --- Stage 1: Exact document hash match ---
        ex_hash = existing.get("document_hash")
        if new_hash and ex_hash and new_hash == ex_hash:
            candidates.append(DuplicateCandidate(
                candidate_invoice_id=ex_id,
                match_type="exact_hash",
                similarity_score=1.0,
                evidence={
                    "method": "Document hash match",
                    "hash": new_hash,
                },
            ))
            seen_ids.add(ex_id)
            continue

        # --- Stage 2: Exact vendor name + invoice number ---
        ex_vendor = existing.get("vendor_name", "")
        ex_inv_num = normalize_invoice_number(existing.get("invoice_number"))
        if new_inv_num and ex_inv_num and new_inv_num == ex_inv_num:
            vendor_sim = string_similarity(new_vendor, ex_vendor)
            if vendor_sim >= 0.9:
                candidates.append(DuplicateCandidate(
                    candidate_invoice_id=ex_id,
                    match_type="exact_vendor_invoice",
                    similarity_score=vendor_sim,
                    evidence={
                        "method": "Exact vendor + invoice number match",
                        "invoice_number": new_invoice.get("invoice_number"),
                        "vendor_similarity": round(vendor_sim, 3),
                    },
                ))
                seen_ids.add(ex_id)
                continue

        # --- Stage 3: Normalized GSTIN + invoice number ---
        ex_gstin = normalize_gstin(existing.get("vendor_gstin"))
        if new_gstin and ex_gstin and new_gstin == ex_gstin:
            if new_inv_num and ex_inv_num and new_inv_num == ex_inv_num:
                candidates.append(DuplicateCandidate(
                    candidate_invoice_id=ex_id,
                    match_type="normalized_gstin_invoice",
                    similarity_score=1.0,
                    evidence={
                        "method": "GSTIN + invoice number match",
                        "gstin": new_invoice.get("vendor_gstin"),
                        "invoice_number": new_invoice.get("invoice_number"),
                    },
                ))
                seen_ids.add(ex_id)
                continue

        # --- Stage 4: GSTIN + amount + date window ---
        if new_gstin and ex_gstin and new_gstin == ex_gstin:
            ex_total = existing.get("grand_total")
            ex_date = existing.get("invoice_date")
            if (
                new_total is not None
                and ex_total is not None
                and abs(float(new_total) - float(ex_total)) < 0.01
            ):
                date_match = True
                if new_date and ex_date:
                    if isinstance(new_date, str):
                        try:
                            new_date = datetime.fromisoformat(new_date)
                        except Exception:
                            date_match = True
                    if isinstance(ex_date, str):
                        try:
                            ex_date = datetime.fromisoformat(ex_date)
                        except Exception:
                            date_match = True
                    if isinstance(new_date, datetime) and isinstance(ex_date, datetime):
                        # Make both offset-naive for comparison
                        nd = new_date.replace(tzinfo=None) if new_date.tzinfo else new_date
                        ed = ex_date.replace(tzinfo=None) if ex_date.tzinfo else ex_date
                        date_match = abs((nd - ed).days) <= date_window_days

                if date_match:
                    candidates.append(DuplicateCandidate(
                        candidate_invoice_id=ex_id,
                        match_type="amount_date_window",
                        similarity_score=0.9,
                        evidence={
                            "method": "GSTIN + amount + date window match",
                            "gstin": new_invoice.get("vendor_gstin"),
                            "amount": float(new_total),
                            "date_window_days": date_window_days,
                        },
                    ))
                    seen_ids.add(ex_id)
                    continue

        # --- Stage 5: Fuzzy field similarity ---
        score_parts = []

        if new_vendor and ex_vendor:
            vendor_sim = string_similarity(new_vendor, ex_vendor)
            score_parts.append(("vendor_name", vendor_sim, 0.3))

        if new_inv_num and ex_inv_num:
            inv_sim = string_similarity(new_inv_num, ex_inv_num)
            score_parts.append(("invoice_number", inv_sim, 0.3))

        if new_total is not None and ex_total is not None:
            max_val = max(abs(float(new_total)), abs(float(ex_total)), 1.0)
            amount_sim = 1.0 - (abs(float(new_total) - float(ex_total)) / max_val)
            amount_sim = max(0.0, amount_sim)
            score_parts.append(("amount", amount_sim, 0.4))

        if score_parts:
            total_weight = sum(w for _, _, w in score_parts)
            if total_weight > 0:
                weighted_score = sum(s * w for _, s, w in score_parts) / total_weight
                if weighted_score >= fuzzy_threshold:
                    candidates.append(DuplicateCandidate(
                        candidate_invoice_id=ex_id,
                        match_type="fuzzy_similarity",
                        similarity_score=round(weighted_score, 4),
                        evidence={
                            "method": "Fuzzy field similarity",
                            "field_scores": {name: round(s, 3) for name, s, _ in score_parts},
                            "weighted_score": round(weighted_score, 4),
                            "threshold": fuzzy_threshold,
                        },
                    ))
                    seen_ids.add(ex_id)

    # Sort by similarity score descending
    candidates.sort(key=lambda c: c.similarity_score, reverse=True)
    return candidates
