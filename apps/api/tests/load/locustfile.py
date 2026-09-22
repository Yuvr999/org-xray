import json
import random
import time
from locust import HttpUser, task, between


class OrgXRayLoadTestUser(HttpUser):
    """
    Simulates enterprise user journeys against ORG-XRAY backend:
    - Authentication and Token Refresh
    - Health & Telemetry checks
    - Demand listing & ML routing requests
    - Process mining event ingestion
    - Invoice list retrieval & metadata checks
    - Assistant AI knowledge search
    """
    wait_time = between(0.5, 2.0)
    token = None
    headers = {}

    def on_start(self):
        # Authenticate test user
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "employee@example.com", "password": "password123"}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(3)
    def check_health_and_metrics(self):
        self.client.get("/api/v1/health")
        self.client.get("/api/v1/metrics")

    @task(4)
    def list_and_route_demands(self):
        if not self.headers:
            return
        # Get demand list
        self.client.get("/api/v1/demands", headers=self.headers)
        
        # Test routing classifier
        sample_descriptions = [
            "Purchase 15 MacBook Pro M3 laptops for engineering team",
            "Renew AWS annual cloud hosting subscription and support",
            "Urgent office supplies, whiteboard markers and printer paper",
            "Consulting services for legal tax audit and compliance review"
        ]
        desc = random.choice(sample_descriptions)
        self.client.post(
            "/api/v1/demands/route",
            json={"description": desc, "estimated_amount": 75000},
            headers=self.headers
        )

    @task(3)
    def stream_process_events(self):
        if not self.headers:
            return
        case_id = f"LOAD-CASE-{random.randint(1000, 9999)}"
        self.client.post(
            "/api/v1/processes/events",
            json={
                "case_id": case_id,
                "activity": random.choice(["demand_created", "purchase_order_issued", "invoice_received", "payment_processed"]),
                "timestamp": "2026-09-22T12:00:00Z",
                "department": "Engineering",
                "actor": "load_agent",
                "attributes": {"channel": "portal", "amount": 15000}
            },
            headers=self.headers
        )

    @task(2)
    def query_procurement_assistant(self):
        if not self.headers:
            return
        self.client.post(
            "/api/v1/assistant/query",
            json={"query": "What is the approval threshold for IT hardware purchase?"},
            headers=self.headers
        )

    @task(2)
    def check_invoices(self):
        if not self.headers:
            return
        self.client.get("/api/v1/invoices", headers=self.headers)
