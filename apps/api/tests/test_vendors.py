import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_vendor_catalog_endpoints(client: AsyncClient):
    # Login employee
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List all vendors
    res = await client.get("/api/v1/vendors", headers=headers)
    assert res.status_code == 200
    vendors = res.json()
    assert len(vendors) >= 2

    # 2. Filter by category
    res_tech = await client.get("/api/v1/vendors?category=Technical", headers=headers)
    assert res_tech.status_code == 200
    tech_vendors = res_tech.json()
    assert all(v["category"] == "Technical" for v in tech_vendors)

    # 3. Get single vendor
    v_id = vendors[0]["id"]
    res_single = await client.get(f"/api/v1/vendors/{v_id}", headers=headers)
    assert res_single.status_code == 200
    assert res_single.json()["id"] == v_id
