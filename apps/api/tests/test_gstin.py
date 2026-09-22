import pytest
from app.services.gstin_service import (
    calculate_mod36_checksum,
    validate_gstin_format,
    MockGSTINAdapter,
    RESTGSTINAdapter,
)


def test_validate_gstin_format():
    # Valid formats
    assert validate_gstin_format("27AAPCU6142R1ZA") is True
    assert validate_gstin_format("07AAAAP9988C1ZD") is True
    assert validate_gstin_format("27AAACT1020A1ZB") is True

    # Invalid formats
    assert validate_gstin_format("INVALID_GSTIN") is False
    assert validate_gstin_format("123456789012345") is False
    assert validate_gstin_format("27AAPCU6142R1Z") is False  # Only 14 chars
    assert validate_gstin_format("") is False


def test_mod36_checksum_calculation():
    # Test MOD-36 calculation algorithm
    is_valid, expected = calculate_mod36_checksum("27AAPCU6142R1ZA")
    assert expected is not None
    
    # Test valid check digit match
    test_gstin = f"27AAPCU6142R1Z{expected}"
    is_valid_test, _ = calculate_mod36_checksum(test_gstin)
    assert is_valid_test is True

    # Test invalid check digit mismatch
    wrong_check_digit = "X" if expected != "X" else "Y"
    invalid_gstin = f"27AAPCU6142R1Z{wrong_check_digit}"
    is_valid_inv, _ = calculate_mod36_checksum(invalid_gstin)
    assert is_valid_inv is False


@pytest.mark.asyncio
async def test_mock_gstin_adapter():
    adapter = MockGSTINAdapter()

    # Active taxpayer mock
    res_active = await adapter.verify_live("27AAPCU6142R1ZA")
    assert res_active.success is True
    assert res_active.status == "ACTIVE"
    assert "ENTERPRISE VENDOR" in res_active.legal_name
    assert res_active.state_code == "27"

    # Inactive taxpayer mock (starts with 99)
    res_inactive = await adapter.verify_live("99AAPCU6142R1ZA")
    assert res_inactive.success is False
    assert res_inactive.status == "INACTIVE"


@pytest.mark.asyncio
async def test_gstin_verify_api_endpoint(client):
    # 1. Login as employee
    login_res = await client.post(
        "/api/v1/auth/session",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify valid GSTIN via API
    # Calculate correct checksum for test vector
    _, expected_digit = calculate_mod36_checksum("27AAPCU6142R1ZA")
    valid_test_gstin = f"27AAPCU6142R1Z{expected_digit}"

    verify_res = await client.post(
        "/api/v1/gstin/verify",
        headers=headers,
        json={"gstin": valid_test_gstin, "skip_live_check": False},
    )
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["gstin"] == valid_test_gstin
    assert v_data["is_format_valid"] is True
    assert v_data["is_checksum_valid"] is True
    assert v_data["is_live_verified"] is True
    assert v_data["status"] == "PROVIDER_VERIFIED"

    # 3. Retrieve cached verification via GET /api/v1/gstin/{gstin}
    get_res = await client.get(f"/api/v1/gstin/{valid_test_gstin}", headers=headers)
    assert get_res.status_code == 200
    g_data = get_res.json()
    assert g_data["gstin"] == valid_test_gstin
    assert g_data["is_checksum_valid"] is True


@pytest.mark.asyncio
async def test_gstin_verify_invalid_checksum_api(client):
    login_res = await client.post(
        "/api/v1/auth/session",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # GSTIN with wrong check digit
    invalid_gstin = "27AAPCU6142R1Z0"
    is_val, expected = calculate_mod36_checksum(invalid_gstin)
    if is_val:  # If 0 happens to be valid, pick another
        invalid_gstin = "27AAPCU6142R1Z9"

    verify_res = await client.post(
        "/api/v1/gstin/verify",
        headers=headers,
        json={"gstin": invalid_gstin},
    )
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["is_format_valid"] is True
    assert v_data["is_checksum_valid"] is False
    assert v_data["status"] == "INVALID_CHECKSUM"
