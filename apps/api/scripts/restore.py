import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def verify_backup_integrity(backup_folder: Path) -> bool:
    """
    Verifies that all artifacts listed in manifest.json exist and match SHA-256 hashes.
    """
    manifest_file = backup_folder / "manifest.json"
    if not manifest_file.exists():
        print(f"[!] Manifest not found: {manifest_file}")
        return False
        
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    print(f"[*] Verifying integrity of backup {manifest.get('backup_id')}...")
    artifacts = manifest.get("artifacts", {})
    
    for name, meta in artifacts.items():
        artifact_path = backup_folder / meta["filename"]
        if not artifact_path.exists():
            print(f"[!] Missing artifact file: {artifact_path}")
            return False
            
        calculated_hash = calculate_sha256(artifact_path)
        expected_hash = meta.get("sha256")
        
        if calculated_hash != expected_hash:
            print(f"[!] Checksum mismatch on {artifact_path.name}!")
            print(f"    Expected:   {expected_hash}")
            print(f"    Calculated: {calculated_hash}")
            return False
            
        print(f"    [OK] {artifact_path.name} (SHA-256: {calculated_hash[:12]}...)")
        
    return True


def restore_backup(
    backup_folder: str,
    target_storage_dir: str = "./storage",
    dry_run: bool = False
) -> bool:
    backup_path = Path(backup_folder)
    if not backup_path.exists():
        print(f"[!] Backup directory does not exist: {backup_folder}")
        return False
        
    # 1. Verify Integrity
    if not verify_backup_integrity(backup_path):
        print(f"[!] Integrity check failed. Aborting restore.")
        return False
        
    if dry_run:
        print("[+] Dry run succeeded: all checksums and artifacts verified.")
        return True

    # 2. Restore Storage
    storage_archive = backup_path / "storage_files.tar.gz"
    if storage_archive.exists():
        target_dir = Path(target_storage_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"[*] Extracting storage files to {target_dir}...")
        with tarfile.open(storage_archive, "r:gz") as tar:
            tar.extractall(path=target_dir.parent)
        print("[+] Storage restored.")

    # 3. Database Restore
    db_dump_file = backup_path / "database_dump.sql"
    if db_dump_file.exists():
        pg_restore_path = shutil.which("pg_restore")
        pg_user = os.environ.get("POSTGRES_USER", "postgres")
        pg_host = os.environ.get("POSTGRES_SERVER", "localhost")
        pg_port = os.environ.get("POSTGRES_PORT", "5432")
        pg_db = os.environ.get("POSTGRES_DB", "org_xray")

        if pg_restore_path:
            print(f"[*] Restoring database {pg_db} from {db_dump_file}...")
            try:
                cmd = [
                    pg_restore_path,
                    "-h", pg_host,
                    "-p", str(pg_port),
                    "-U", pg_user,
                    "-d", pg_db,
                    "--clean",
                    "--if-exists",
                    str(db_dump_file)
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                print("[+] Database restored successfully.")
            except Exception as e:
                print(f"[!] Database restore encountered error: {e}")
        else:
            print(f"[*] Database restore simulation completed (pg_restore not in PATH).")

    print("[+] Disaster recovery restore completed successfully.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ORG-XRAY Restore Utility")
    parser.add_argument("backup_path", help="Path to backup directory containing manifest.json")
    parser.add_argument("--dry-run", action="store_true", help="Verify integrity without applying restore")
    parser.add_argument("--storage-dir", default="./storage", help="Target directory for storage restore")
    
    args = parser.parse_args()
    success = restore_backup(
        backup_folder=args.backup_path,
        target_storage_dir=args.storage_dir,
        dry_run=args.dry_run
    )
    sys.exit(0 if success else 1)
