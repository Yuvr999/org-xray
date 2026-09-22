import pytest
from app.services.process_service import calculate_shadow_score, get_score_band
from app.models.process import ProcessEvent


def test_shadow_score_bands():
    assert get_score_band(25.0) == "Normal"
    assert get_score_band(45.0) == "Process Variation"
    assert get_score_band(75.0) == "Suspicious"
    assert get_score_band(92.0) == "Strong Shadow Process"


def test_shadow_score_math():
    expected_activities = ["request_approval", "po_created", "invoice_received", "payment_processed"]
    events = [
        ProcessEvent(
            case_id="CASE-101",
            activity="manual_purchase_tracking",
            activity_category="unapproved",
            source_system="Excel Spreadsheet",
            actor_role="employee",
            amount=15000.0,
        ),
        ProcessEvent(
            case_id="CASE-101",
            activity="bypassed_gateway_api",
            activity_category="unapproved",
            source_system="Personal Card",
            actor_role="external",
            amount=5000.0,
        ),
    ]

    score, components, missing, unexpected, repeated = calculate_shadow_score(events, expected_activities)

    # Verify score formula calculation:
    # 0.25*Deviation + 0.20*Recurrence + 0.15*Consistency + 0.15*CrossSystem + 0.25*BusinessRisk
    expected_score = round(
        (0.25 * components.deviation)
        + (0.20 * components.recurrence)
        + (0.15 * components.consistency)
        + (0.15 * components.cross_system_activity)
        + (0.25 * components.business_risk),
        2,
    )
    assert score == expected_score
    assert score > 60.0  # Suspicious or Strong Shadow Process
    assert "request_approval" in missing
    assert "manual_purchase_tracking" in unexpected


@pytest.mark.asyncio
async def test_process_event_ingestion_and_analysis(client):
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    admin_token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Ingest normal event
    e1_resp = await client.post(
        "/api/v1/process-events",
        headers=headers,
        json={
            "case_id": "CASE-9001",
            "source_system": "ERP",
            "process_name": "SaaS Subscription Procurement",
            "activity": "request_approval",
            "activity_category": "procurement",
            "amount": 1200.0,
        },
    )
    assert e1_resp.status_code == 201

    # 2. Ingest unapproved shadow event
    e2_resp = await client.post(
        "/api/v1/process-events",
        headers=headers,
        json={
            "case_id": "CASE-9001",
            "source_system": "Personal Credit Card Claim",
            "process_name": "SaaS Subscription Procurement",
            "activity": "manual_saas_ingestion",
            "activity_category": "unapproved_software",
            "amount": 14200.0,
        },
    )
    assert e2_resp.status_code == 201

    # 3. Analyze case
    analyze_resp = await client.post(
        "/api/v1/process-events/analyze?department=Marketing",
        headers=headers,
        json={"case_id": "CASE-9001"},
    )
    assert analyze_resp.status_code == 200
    analysis_data = analyze_resp.json()
    assert analysis_data["case_id"] == "CASE-9001"
    assert analysis_data["shadow_score"] > 30.0
    assert analysis_data["alert_created"] is True
    alert_id = analysis_data["alert_id"]

    # 4. List shadow alerts
    alerts_resp = await client.get("/api/v1/shadow-alerts", headers=headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1

    # 5. Submit feedback
    fb_resp = await client.post(
        f"/api/v1/shadow-alerts/{alert_id}/feedback",
        headers=headers,
        json={
            "feedback_label": "Valid Shadow Process",
            "notes": "Confirmed unsanctioned analytics SaaS subscription.",
        },
    )
    assert fb_resp.status_code == 200
    fb_data = fb_resp.json()
    assert fb_data["feedback_label"] == "Valid Shadow Process"
