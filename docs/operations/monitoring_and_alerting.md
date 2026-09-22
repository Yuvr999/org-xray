# Monitoring and Alerting Runbook

## 1. Observability Architecture
- **Metrics Endpoint**: `GET /api/v1/metrics` provides runtime telemetry, uptime, database/Redis status, and alert summary.
- **Alert Stream**: `GET /api/v1/metrics/alerts?min_severity=WARNING` retrieves recent operational alerts from the in-memory ring buffer.
- **Health & Readiness**: 
  - `GET /api/v1/health` (Liveness check for orchestrators / kubernetes).
  - `GET /api/v1/ready` (Readiness check verifying DB and Redis availability).

---

## 2. Core Operational Metrics & Thresholds

| Metric | Target / SLA | Warning Threshold | Critical Threshold |
|--------|--------------|-------------------|--------------------|
| API Uptime | > 99.9% | < 99.5% | < 99.0% |
| p95 Latency | < 150ms | > 300ms | > 1000ms |
| HTTP 5xx Error Rate | < 0.1% | > 1.0% | > 5.0% |
| DB Connection Pool | < 70% used | > 80% used | > 95% used |
| Redis Connection | Active | Degraded | Down |
| GSTIN Outages | 0 | 3 consecutive failures | 10 consecutive failures |
| Shadow Score Anomaly Spikes | Baseline | > 5 anomalies / min | > 20 anomalies / min |

---

## 3. Alert Routing & Sinks
- **CRITICAL**: PagerDuty / On-call engineer immediate notification + Webhook.
- **ERROR**: Slack `#alerts-error` channel + log entry.
- **WARNING**: Slack `#alerts-warning` channel + log entry.
- **INFO**: System log stream.
