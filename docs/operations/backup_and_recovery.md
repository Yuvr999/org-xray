# Backup and Disaster Recovery Runbook

## Overview
This runbook details standard operating procedures for taking, verifying, and restoring backups for ORG-XRAY PostgreSQL database and object storage artifacts.

---

## 1. Targets & Objectives
- **Recovery Point Objective (RPO)**: < 1 hour.
- **Recovery Time Objective (RTO)**: < 30 minutes.
- **Retention Schedule**:
  - Daily snapshots retained for 30 days.
  - Weekly snapshots retained for 90 days.
  - Monthly snapshots retained for 1 year.

---

## 2. Automated Backup Execution

### Running an On-Demand Backup
Execute the backup script from the API service directory:
```bash
python scripts/backup.py --output /var/backups/org_xray --retention-days 30
```

### Generated Artifacts
Each backup run produces a timestamped folder containing:
1. `database_dump.sql` (Custom format compressed PostgreSQL dump).
2. `storage_files.tar.gz` (Archive of uploaded invoice documents and files).
3. `manifest.json` (SHA-256 integrity checksums and metadata).

---

## 3. Disaster Recovery & Restore Procedure

### Step 1: Pre-flight Integrity Verification (Dry Run)
Before restoring, verify that no backup artifacts have been corrupted:
```bash
python scripts/restore.py /var/backups/org_xray/backup_YYYYMMDD_HHMMSS --dry-run
```

### Step 2: Target Service Preparation
1. Stop incoming API write traffic (enable maintenance mode on reverse proxy).
2. Ensure database user has administrative privileges to recreate tables.

### Step 3: Execute Restore
```bash
python scripts/restore.py /var/backups/org_xray/backup_YYYYMMDD_HHMMSS --storage-dir ./storage
```

### Step 4: Post-Restore Health Verification
Run health checks to confirm database and storage accessibility:
```bash
curl -f http://localhost:8000/api/v1/ready
python -m pytest tests/test_health.py
```
