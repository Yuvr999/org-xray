# Incident Response Runbook

## Severity Classification

| Level | Name | Definition | Response Time |
|-------|------|------------|---------------|
| SEV-1 | Critical | Complete service outage, data loss, or security breach | 15 minutes |
| SEV-2 | High | Partial service degradation affecting business workflows | 30 minutes |
| SEV-3 | Medium | Non-critical feature impaired, workaround available | 2 hours |
| SEV-4 | Low | Minor issue, cosmetic bug, or informational anomaly | Next business day |

---

## On-Call Escalation Matrix

| Tier | Who | When Paged |
|------|-----|------------|
| L1 | Backend On-call Engineer | SEV-1, SEV-2 immediately |
| L2 | Engineering Lead | SEV-1 immediately; SEV-2 after 30 min no resolution |
| L3 | Platform VP / CTO | SEV-1 unresolved after 60 min |
| Legal / Data | DPO | Any confirmed security breach or data leak |

---

## Initial Response Protocol

### SEV-1 Checklist
```
[ ] Declare incident in #incidents Slack channel with timestamp
[ ] Page L1 on-call via PagerDuty
[ ] Confirm scope: which services affected, how many users
[ ] Begin impact logging in incident doc
[ ] Check /api/v1/ready for dependency health
[ ] Check /api/v1/metrics/alerts for recent critical alerts
[ ] Decide: roll back or hotfix?
```

### Common Diagnostic Commands
```bash
# Check API health and dependency status
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:8000/api/v1/ready

# Check recent critical/error alerts
curl http://localhost:8000/api/v1/metrics/alerts?min_severity=ERROR

# Check running container logs
docker logs org-xray-prod-api --since 15m

# Check database connectivity
docker exec org-xray-prod-db pg_isready -U postgres

# Check Redis connectivity
docker exec org-xray-prod-redis redis-cli ping
```

---

## Post-Mortem / RCA Template

**Incident Title:** _______________  
**Date:** _______________  
**Severity:** SEV-___  
**Duration (Minutes):** _______________  
**Incident Commander:** _______________  

### Timeline
| Time (UTC) | Action / Observation |
|------------|---------------------|
| HH:MM | |

### Root Cause
_Describe the direct and contributing causes._

### Impact
- Services affected:
- Users impacted (estimated count):
- Data affected:

### What Went Well
_Items that helped contain or resolve the incident faster._

### What Went Wrong
_Items that contributed to impact severity or delayed resolution._

### Action Items

| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| | | | |

---

## Communication Playbooks

### External Status Page Update (SEV-1/SEV-2)
```
Subject: [STATUS UPDATE] ORG-XRAY Service Degradation — {timestamp}

We are currently investigating an issue affecting {service}. 
Engineering is actively working on resolution.

Impact: {describe scope}
Started at: {time UTC}
Next update: {time UTC + 30 min}
```

### Resolution Announcement
```
Subject: [RESOLVED] ORG-XRAY Service Restored — {timestamp}

The incident affecting {service} has been resolved at {time UTC}.

Root cause: {brief summary}
Duration: {N} minutes
Action taken: {brief summary}

Full post-mortem will be published within 48 hours.
```
