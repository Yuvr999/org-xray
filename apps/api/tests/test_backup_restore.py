import json
import os
import shutil
from pathlib import Path
import pytest
from scripts.backup import create_backup, calculate_sha256
from scripts.restore import verify_backup_integrity, restore_backup


def test_backup_and_restore_cycle(tmp_path):
    # Setup dummy storage
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    sample_file = storage_dir / "sample_invoice.pdf"
    sample_file.write_text("dummy invoice content for backup testing")

    os.environ["LOCAL_STORAGE_DIR"] = str(storage_dir)

    backup_dir = tmp_path / "backups"
    
    # 1. Run backup
    manifest = create_backup(
        output_dir=str(backup_dir),
        include_storage=True,
        retention_days=7
    )
    
    backup_folder = backup_dir / manifest["backup_id"]
    assert backup_folder.exists()
    assert (backup_folder / "manifest.json").exists()
    assert (backup_folder / "database_dump.sql").exists()
    assert (backup_folder / "storage_files.tar.gz").exists()
    
    # 2. Test Integrity Verification
    assert verify_backup_integrity(backup_folder) is True

    # 3. Test Tamper Detection
    storage_archive = backup_folder / "storage_files.tar.gz"
    with open(storage_archive, "ab") as f:
        f.write(b"corrupted bytes")
    assert verify_backup_integrity(backup_folder) is False

    # 4. Create fresh clean backup
    manifest_clean = create_backup(
        output_dir=str(backup_dir),
        include_storage=True,
        retention_days=7
    )
    clean_backup_folder = backup_dir / manifest_clean["backup_id"]
    
    # 5. Test Dry-Run Restore
    restore_target = tmp_path / "restored_storage"
    assert restore_backup(
        backup_folder=str(clean_backup_folder),
        target_storage_dir=str(restore_target),
        dry_run=True
    ) is True

    # 6. Test Live Restore
    assert restore_backup(
        backup_folder=str(clean_backup_folder),
        target_storage_dir=str(restore_target),
        dry_run=False
    ) is True
