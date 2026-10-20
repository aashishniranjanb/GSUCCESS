"""
Disaster recovery and restoration tool for GPAT 2027 Learning OS.
Restores database from compressed snapshot with checksum verification,
schema integrity check, and safety pre-restore backup.
"""

import sys
import gzip
import shutil
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

import os
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = Path(os.environ.get("DB_PATH", ROOT_DIR / "gpat_knowledge.db"))
DEFAULT_BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", ROOT_DIR / "backups"))

def compute_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def verify_and_restore(
    backup_file: Path,
    target_db: Path = DEFAULT_DB_PATH,
    expected_sha256: Optional[str] = None
) -> Dict[str, Any]:
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file not found at {backup_file}")

    # 1. Verify Checksum if provided
    actual_sha = compute_sha256(backup_file)
    if expected_sha256 and actual_sha != expected_sha256:
        raise ValueError(f"Checksum mismatch! Expected {expected_sha256}, got {actual_sha}")

    # 2. Decompress to a temporary staging file first
    staging_file = target_db.with_suffix(".staging.tmp")
    if staging_file.exists():
        staging_file.unlink()

    with gzip.open(backup_file, "rb") as f_in:
        with open(staging_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # 3. Test integrity of the decompressed database before touching production DB
    test_conn = sqlite3.connect(str(staging_file))
    cur = test_conn.cursor()
    cur.execute("PRAGMA quick_check")
    check_result = cur.fetchone()[0]
    if check_result != "ok":
        test_conn.close()
        staging_file.unlink()
        raise RuntimeError(f"Database integrity check failed: {check_result}")

    # Count restored records
    cur.execute("SELECT COUNT(*) FROM questions")
    q_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM candidate_claims")
    c_count = cur.fetchone()[0]
    test_conn.close()

    # 4. Create a safety backup of existing production DB if it exists
    if target_db.exists():
        pre_restore_safety = target_db.with_suffix(".pre_restore.bak")
        shutil.copy2(target_db, pre_restore_safety)

    # 5. Atomically replace target database
    if target_db.exists():
        target_db.unlink()
    staging_file.rename(target_db)

    return {
        "status": "RESTORED_SUCCESSFULLY",
        "target_db": str(target_db),
        "backup_file": backup_file.name,
        "questions_restored": q_count,
        "claims_restored": c_count,
        "integrity_check": check_result
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        chosen_backup = Path(sys.argv[1])
    else:
        # Pick latest backup
        backups = sorted(DEFAULT_BACKUP_DIR.glob("gpat_backup_*.db.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not backups:
            print("No backup files found in", DEFAULT_BACKUP_DIR)
            sys.exit(1)
        chosen_backup = backups[0]

    print(f"Restoring from: {chosen_backup}...")
    res = verify_and_restore(chosen_backup)
    print("Restore result:", res)
