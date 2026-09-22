import pytest
from datetime import datetime, timezone
from app.services.duplicate_detection import find_duplicates, normalize_gstin, normalize_invoice_number


def test_normalize_gstin():
    assert normalize_gstin(" 27AABCT3518Q1Z6 ") == "27AABCT3518Q1Z6"
    assert normalize_gstin("27-aabct-3518-q1z6") == "27AABCT3518Q1Z6"
    assert normalize_gstin(None) is None


def test_normalize_invoice_number():
    assert normalize_invoice_number(" INV-2024/001 ") == "INV2024001"
    assert normalize_invoice_number("inv_2024_001") == "INV2024001"
    assert normalize_invoice_number(None) is None


def test_exact_hash_duplicate():
    new_invoice = {
        "id": 10,
        "document_hash": "abc123hash",
        "vendor_name": "ACME Corp",
        "vendor_gstin": "27AABCT3518Q1Z6",
        "invoice_number": "INV-001",
        "grand_total": 5000.0,
    }
    existing_invoices = [
        {
            "id": 1,
            "document_hash": "abc123hash",
            "vendor_name": "Different Name",
            "vendor_gstin": "27AABCT3518Q1Z6",
            "invoice_number": "INV-999",
            "grand_total": 1000.0,
        }
    ]
    candidates = find_duplicates(new_invoice, existing_invoices)
    assert len(candidates) == 1
    assert candidates[0].match_type == "exact_hash"
    assert candidates[0].candidate_invoice_id == 1
    assert candidates[0].similarity_score == 1.0


def test_exact_vendor_and_number_duplicate():
    new_invoice = {
        "id": 10,
        "document_hash": "newhash1",
        "vendor_name": "Acme Technologies Pvt Ltd",
        "vendor_gstin": None,
        "invoice_number": "INV/2026/101",
        "grand_total": 12000.0,
    }
    existing_invoices = [
        {
            "id": 2,
            "document_hash": "oldhash2",
            "vendor_name": "Acme Technologies Pvt Ltd",
            "vendor_gstin": None,
            "invoice_number": "INV-2026-101",
            "grand_total": 12000.0,
        }
    ]
    candidates = find_duplicates(new_invoice, existing_invoices)
    assert len(candidates) == 1
    assert candidates[0].match_type == "exact_vendor_invoice"
    assert candidates[0].candidate_invoice_id == 2


def test_gstin_and_number_duplicate():
    new_invoice = {
        "id": 10,
        "document_hash": "newhash",
        "vendor_name": "Vendor A",
        "vendor_gstin": "29ABCDE1234F1Z5",
        "invoice_number": "INV-999",
        "grand_total": 500.0,
    }
    existing_invoices = [
        {
            "id": 3,
            "document_hash": "otherhash",
            "vendor_name": "Vendor A Alternate Name",
            "vendor_gstin": "29ABCDE1234F1Z5",
            "invoice_number": "INV-999",
            "grand_total": 500.0,
        }
    ]
    candidates = find_duplicates(new_invoice, existing_invoices)
    assert len(candidates) == 1
    assert candidates[0].match_type == "normalized_gstin_invoice"
    assert candidates[0].candidate_invoice_id == 3


def test_amount_date_window_duplicate():
    new_invoice = {
        "id": 10,
        "document_hash": "hash10",
        "vendor_name": "Tata Power",
        "vendor_gstin": "27AABCT3518Q1Z6",
        "invoice_number": "TP-002",
        "grand_total": 45000.0,
        "invoice_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
    }
    existing_invoices = [
        {
            "id": 4,
            "document_hash": "hash4",
            "vendor_name": "Tata Power",
            "vendor_gstin": "27AABCT3518Q1Z6",
            "invoice_number": "TP-001",
            "grand_total": 45000.0,
            "invoice_date": datetime(2026, 9, 15, tzinfo=timezone.utc),
        }
    ]
    candidates = find_duplicates(new_invoice, existing_invoices, date_window_days=30)
    assert len(candidates) == 1
    assert candidates[0].match_type == "amount_date_window"
    assert candidates[0].candidate_invoice_id == 4
