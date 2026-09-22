# Deployment and Release Runbook

## 1. Release Gating Checklist
Before deploying to staging or production, ensure:
- [ ] All unit and integration tests pass (`pytest`).
- [ ] Security scanners pass with 0 high/critical issues (`bandit`, `safety`).
- [ ] Pre-flight database migrations run cleanly against test DB (`alembic upgrade head`).
- [ ] Docker images build cleanly with non-root runtime verified.
- [ ] Automated pre-deployment backup completed.

---

## 2. Staging Deployment Procedure
1. Trigger staging deploy pipeline via GitHub Actions or run:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
2. Verify migrations:
   ```bash
   docker exec org-xray-prod-api alembic upgrade head
   ```
3. Verify readiness:
   ```bash
   curl -f http://staging.internal:8000/api/v1/ready
   ```

---

## 3. Production Deployment & Zero-Downtime Migration
1. Take pre-release backup:
   ```bash
   python apps/api/scripts/backup.py --output /var/backups/org_xray
   ```
2. Apply backward-compatible migrations:
   ```bash
   alembic upgrade head
   ```
3. Deploy new API containers using rolling / blue-green rollout.
4. Perform smoke test on `/api/v1/health` and `/api/v1/metrics`.

---

## 4. Rollback Procedure
If critical errors or regressions occur post-release:
1. Revert container image tag to previous stable release.
2. If database schema rollback is required:
   ```bash
   alembic downgrade -1
   ```
3. If database state is corrupted, execute disaster recovery restore:
   ```bash
   python apps/api/scripts/restore.py /var/backups/org_xray/backup_PRE_RELEASE
   ```
