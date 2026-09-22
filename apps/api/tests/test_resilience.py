import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.services.llm_gateway import llm_gateway
from app.services.gstin_service import RESTGSTINAdapter
from app.core.rate_limit import RateLimiter
from app.services.alerting_service import alerting_service, AlertSeverity


@pytest.mark.asyncio
async def test_security_headers_and_correlation_id(client: AsyncClient):
    """
    Verifies that security headers and X-Request-ID are attached to API responses.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    
    headers = response.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers
    assert "X-Request-ID" in headers
    assert "X-Process-Time-Ms" in headers


@pytest.mark.asyncio
async def test_gstin_provider_outage_fallback():
    """
    Verifies that when an external REST GSTIN provider throws an exception (503/timeout),
    the adapter handles the error safely and returns a failed verification payload.
    """
    adapter = RESTGSTINAdapter(api_url="https://mock-gst-provider.com/api", api_key="secret-key")
    
    with patch("httpx.AsyncClient.get", side_effect=Exception("Provider timeout / Gateway Down")):
        res = await adapter.verify_live("27AAPCU6142R1ZA")
        assert res.success is False
        assert res.status == "PROVIDER_UNAVAILABLE"
        assert "Provider timeout" in res.error_message


@pytest.mark.asyncio
async def test_llm_gateway_outage_fallback():
    """
    Verifies that when LLM provider throws an exception or fails, structured generation
    falls back cleanly to deterministic fallback text without crashing.
    """
    with patch("httpx.AsyncClient.post", side_effect=Exception("Gemini API connection error")):
        response = await llm_gateway.generate_response(
            prompt_id="procurement_assistant/v1",
            user_message="Emergency purchase inquiry",
        )
        assert "response" in response
        assert len(response["response"]) > 0
        assert "latency_ms" in response


@pytest.mark.asyncio
async def test_rate_limiter_memory_fallback():
    """
    Verifies that rate limiter functions properly using in-memory fallback when Redis is unavailable.
    """
    from starlette.requests import Request
    
    limiter = RateLimiter(default_limit=3, window_seconds=10)
    
    # Create mock request with in-memory IP
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/test",
        "headers": [],
        "client": ("192.168.1.100", 12345),
    }
    req = Request(scope)
    
    # With Redis disabled/mocked to None
    with patch("app.core.rate_limit.get_redis_client", return_value=None):
        # 1st request -> ok
        limited, remaining, _ = await limiter.is_rate_limited(req, limit=3, window=10)
        assert limited is False
        assert remaining == 2
        
        # 2nd request -> ok
        limited, remaining, _ = await limiter.is_rate_limited(req, limit=3, window=10)
        assert limited is False
        assert remaining == 1
        
        # 3rd request -> ok
        limited, remaining, _ = await limiter.is_rate_limited(req, limit=3, window=10)
        assert limited is False
        assert remaining == 0
        
        # 4th request -> limited!
        limited, remaining, retry_after = await limiter.is_rate_limited(req, limit=3, window=10)
        assert limited is True
        assert remaining == 0
        assert retry_after > 0


@pytest.mark.asyncio
async def test_alerting_service_and_metrics_endpoint(client: AsyncClient):
    """
    Verifies operational alert dispatch and telemetry aggregation.
    """
    # Emit test alerts
    await alerting_service.emit_alert(
        title="High Anomaly Rate Detected",
        severity=AlertSeverity.WARNING,
        message="Process anomaly threshold exceeded 80%",
        source_module="process_intelligence",
        details={"case_id": "REQ-101", "shadow_score": 85}
    )

    await alerting_service.emit_alert(
        title="Database Latency Spike",
        severity=AlertSeverity.ERROR,
        message="Query execution time exceeded 2000ms",
        source_module="database",
        details={"query": "SELECT * FROM invoices"}
    )
    
    # Check metrics endpoint
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "dependencies" in data
    assert data["alert_summary"]["WARNING"] >= 1
    assert data["alert_summary"]["ERROR"] >= 1

    # Check alerts listing
    alerts_response = await client.get("/api/v1/metrics/alerts?min_severity=WARNING")
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()
    assert len(alerts) >= 2
    titles = [a["title"] for a in alerts]
    assert "High Anomaly Rate Detected" in titles
    assert "Database Latency Spike" in titles
