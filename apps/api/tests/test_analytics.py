import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_endpoints(client: AsyncClient):
    # 1. Login as Admin
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    assert admin_login.status_code == 200
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Overview Analytics
    overview_res = await client.get("/api/v1/analytics/overview?window=30d", headers=headers)
    assert overview_res.status_code == 200
    overview_data = overview_res.json()
    assert overview_data["time_window"] == "30d"
    assert "composite_shadow_risk_index" in overview_data
    assert "total_approved_spend" in overview_data
    assert "invoice_verification_pass_rate" in overview_data

    # 3. Procurement Analytics
    proc_res = await client.get("/api/v1/analytics/procurement?window=30d", headers=headers)
    assert proc_res.status_code == 200
    proc_data = proc_res.json()
    assert "purchase_request_volume" in proc_data
    assert "total_approved_amount" in proc_data
    assert "category_spend" in proc_data

    # 4. Process Analytics
    proc_mining_res = await client.get("/api/v1/analytics/processes?window=30d", headers=headers)
    assert proc_mining_res.status_code == 200
    proc_mining_data = proc_mining_res.json()
    assert "total_cases_analyzed" in proc_mining_data
    assert "shadow_process_rate" in proc_mining_data

    # 5. Model Performance Analytics
    model_res = await client.get("/api/v1/analytics/model-performance?window=30d", headers=headers)
    assert model_res.status_code == 200
    model_data = model_res.json()
    assert "routing_classifier" in model_data
    assert "shadow_anomaly_detector" in model_data
    assert "overall_human_override_rate" in model_data

    # 6. Audit Summary Analytics
    audit_res = await client.get("/api/v1/analytics/audit-summary?window=30d", headers=headers)
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert "total_audit_events" in audit_data
    assert "actions_breakdown" in audit_data
