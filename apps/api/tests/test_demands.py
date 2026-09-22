import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_demand_full_lifecycle(client: AsyncClient):
    # 1. Login as Employee (emp@test.com / EmpPass123!)
    emp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    assert emp_login.status_code == 200
    emp_token = emp_login.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # 2. Login as Manager (mgr@test.com / MgrPass123!)
    mgr_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "mgr@test.com", "password": "MgrPass123!"},
    )
    assert mgr_login.status_code == 200
    mgr_token = mgr_login.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    # 3. Create Demand
    create_res = await client.post(
        "/api/v1/demands",
        json={
            "title": "GPU Server Infrastructure Cluster",
            "description": "5x NVIDIA H100 GPU servers for machine learning model training",
            "category": "Technical",
            "estimated_amount": 45000.0,
        },
        headers=emp_headers,
    )
    assert create_res.status_code == 201
    demand_data = create_res.json()
    demand_id = demand_data["id"]
    assert demand_data["status"] == "DRAFT"

    # 4. Classify Demand
    classify_res = await client.post(
        f"/api/v1/demands/{demand_id}/classify",
        headers=emp_headers,
    )
    assert classify_res.status_code == 200
    classified_data = classify_res.json()
    assert classified_data["routed_department"] == "Technical"
    assert classified_data["routing_confidence"] is not None
    assert classified_data["status"] == "CLASSIFIED"

    # 5. Submit Demand
    submit_res = await client.post(
        f"/api/v1/demands/{demand_id}/submit",
        headers=emp_headers,
    )
    assert submit_res.status_code == 200
    submitted_data = submit_res.json()
    assert submitted_data["status"] == "PENDING_APPROVAL"
    assert len(submitted_data["approvals"]) == 1
    assert submitted_data["approvals"][0]["status"] == "PENDING"

    # 6. Approve Demand as Manager
    approve_res = await client.post(
        f"/api/v1/demands/{demand_id}/approve",
        json={"comments": "Budget approved for Q4 AI infrastructure"},
        headers=mgr_headers,
    )
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "APPROVED"
    assert approved_data["approvals"][0]["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_demand_purchase_limit_exceeded(client: AsyncClient):
    # Login employee
    emp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    assert emp_login.status_code == 200
    emp_token = emp_login.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Create Demand exceeding department limit (limit is $100,000 for Finance department)
    create_res = await client.post(
        "/api/v1/demands",
        json={
            "title": "Supercomputer Procurement",
            "description": "Massive datacenter hardware overhaul",
            "category": "Technical",
            "estimated_amount": 500000.0,
        },
        headers=emp_headers,
    )
    assert create_res.status_code == 201
    demand_id = create_res.json()["id"]

    # Attempt to submit - should fail with HTTP 400 Purchase Limit Exceeded
    submit_res = await client.post(
        f"/api/v1/demands/{demand_id}/submit",
        headers=emp_headers,
    )
    assert submit_res.status_code == 400
    assert "exceeds department purchase limit" in submit_res.json()["detail"]


@pytest.mark.asyncio
async def test_demand_rejection_flow(client: AsyncClient):
    # Employee login
    emp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    assert emp_login.status_code == 200
    emp_headers = {"Authorization": f"Bearer {emp_login.json()['access_token']}"}

    # Manager login
    mgr_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "mgr@test.com", "password": "MgrPass123!"},
    )
    assert mgr_login.status_code == 200
    mgr_headers = {"Authorization": f"Bearer {mgr_login.json()['access_token']}"}

    # Create & Submit demand
    create_res = await client.post(
        "/api/v1/demands",
        json={
            "title": "Luxury PR Event Sponsorship",
            "description": "Sponsorship of overseas luxury media banquet",
            "category": "PR",
            "estimated_amount": 25000.0,
        },
        headers=emp_headers,
    )
    demand_id = create_res.json()["id"]

    await client.post(f"/api/v1/demands/{demand_id}/submit", headers=emp_headers)

    # Reject demand
    reject_res = await client.post(
        f"/api/v1/demands/{demand_id}/reject",
        json={"comments": "Unjustified expenses for current quarter budget"},
        headers=mgr_headers,
    )
    assert reject_res.status_code == 200
    rejected_data = reject_res.json()
    assert rejected_data["status"] == "REJECTED"
    assert rejected_data["approvals"][0]["status"] == "REJECTED"
