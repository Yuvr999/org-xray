import pytest
import io
from app.services.invoice_extraction import compute_document_hash, extract_fields_from_text
from app.services.tax_validation import validate_gst_arithmetic
from app.services.duplicate_detection import find_duplicates


@pytest.mark.asyncio
async def test_compute_document_hash():
    content = b"Sample Invoice Text Data 12345"
    h1 = compute_document_hash(content)
    h2 = compute_document_hash(content)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex string length


@pytest.mark.asyncio
async def test_extract_fields_from_text():
    sample_text = """
    TAX INVOICE
    Vendor: ACME SOLUTIONS PRIVATE LIMITED
    GSTIN: 27AAPCU6142R1ZA
    Invoice No: INV-2026-0042
    Date: 15/09/2026
    
    Subtotal: 10000.00
    Tax: 1800.00
    Total Amount: 11800.00
    PO Ref: PO-998822
    """
    fields = extract_fields_from_text(sample_text)
    assert fields.vendor_gstin == "27AAPCU6142R1ZA"
    assert fields.invoice_number == "INV-2026-0042"
    assert fields.subtotal == 10000.00
    assert fields.total_tax == 1800.00
    assert fields.grand_total == 11800.00
    assert fields.confidence > 0.6


@pytest.mark.asyncio
async def test_tax_validation_arithmetic():
    # Correct 18% tax
    results = validate_gst_arithmetic(subtotal=10000.0, total_tax=1800.0, grand_total=11800.0, tax_rate=18.0)
    for r in results:
        assert r.passed is True

    # Incorrect total tax
    results_wrong = validate_gst_arithmetic(subtotal=10000.0, total_tax=2500.0, grand_total=12500.0, tax_rate=18.0)
    passed_status = [r.passed for r in results_wrong]
    assert False in passed_status


@pytest.mark.asyncio
async def test_duplicate_detection_logic():
    new_inv = {
        "id": 10,
        "document_hash": "hash_abc_123",
        "vendor_name": "ACME CORP",
        "vendor_gstin": "27AAPCU6142R1ZA",
        "invoice_number": "INV-100",
        "grand_total": 50000.0,
        "invoice_date": None,
    }

    existing = [
        {
            "id": 1,
            "document_hash": "hash_abc_123",  # Exact hash duplicate
            "vendor_name": "ACME CORP",
            "vendor_gstin": "27AAPCU6142R1ZA",
            "invoice_number": "INV-100",
            "grand_total": 50000.0,
            "invoice_date": None,
        }
    ]

    candidates = find_duplicates(new_inv, existing)
    assert len(candidates) >= 1
    assert candidates[0].candidate_invoice_id == 1
    assert candidates[0].match_type == "exact_hash"
    assert candidates[0].similarity_score == 1.0


@pytest.mark.asyncio
async def test_invoice_upload_api_flow(client):
    # 1. Login as employee
    login_res = await client.post(
        "/api/v1/auth/session",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload dummy invoice PDF
    invoice_content = b"""
    TAX INVOICE
    Vendor: TECH SUPPLIES INDIA LTD
    GSTIN: 27AAAAC1234A1Z5
    Invoice No: INV-8899
    Date: 2026-09-01
    Subtotal: 20000.00
    Tax: 3600.00
    Grand Total: 23600.00
    """

    files = {"file": ("invoice_8899.pdf", io.BytesIO(invoice_content), "application/pdf")}
    upload_res = await client.post("/api/v1/invoices?auto_process=true", headers=headers, files=files)
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["id"] is not None
    assert data["vendor_gstin"] == "27AAAAC1234A1Z5"
    assert data["invoice_number"] == "INV-8899"
    assert data["grand_total"] == 23600.00

    invoice_id = data["id"]

    # 3. Get invoice detail
    detail_res = await client.get(f"/api/v1/invoices/{invoice_id}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == invoice_id
    assert len(detail["extractions"]) >= 1

    # 4. List invoices
    list_res = await client.get("/api/v1/invoices", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1

    # 5. Manager reviews invoice
    mgr_login = await client.post(
        "/api/v1/auth/session",
        json={"email": "mgr@test.com", "password": "MgrPass123!"},
    )
    mgr_token = mgr_login.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    review_res = await client.post(
        f"/api/v1/invoices/{invoice_id}/review",
        headers=mgr_headers,
        json={"action": "verify", "notes": "Verified against PO"},
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "VERIFIED"
