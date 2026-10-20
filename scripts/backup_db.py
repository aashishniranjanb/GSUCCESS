"""
Automated SQLite snapshot and backup manager for GPAT 2027 Learning OS.
Ensures zero data loss for learner history, FSRS state, sessions, and knowledge.
Features:
- Online SQLite backup via sqlite3.Connection.backup() (ACID safe, non-blocking)
- SHA-256 integrity checksum generation
- Gzip compression (.db.gz)
- Metadata manifest with table row counts and file sizes
- Retention rotation (defaults to 7 latest snapshots)
"""

import os
import sys
import gzip
import shutil
import sqlite3
import hashlib
import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = Path(os.environ.get("DB_PATH", ROOT_DIR / "gpat_knowledge.db"))
DEFAULT_BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", ROOT_DIR / "backups"))

def compute_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def get_table_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    counts = {}
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = cur.fetchone()[0]
        except Exception:
            counts[t] = -1
    return counts

def create_backup(
    db_path: Path = DEFAULT_DB_PATH,
    backup_dir: Path = DEFAULT_BACKUP_DIR,
    retention_count: int = 7
) -> Dict[str, Any]:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    temp_raw_backup = backup_dir / f"gpat_backup_{timestamp_str}.db"
    compressed_backup = backup_dir / f"gpat_backup_{timestamp_str}.db.gz"

    # 1. Non-blocking SQLite online backup API
    src_conn = sqlite3.connect(str(db_path))
    dst_conn = sqlite3.connect(str(temp_raw_backup))
    with dst_conn:
        src_conn.backup(dst_conn)
    
    # 2. Extract database integrity & table counts
    table_counts = get_table_counts(dst_conn)
    raw_size_bytes = temp_raw_backup.stat().st_size
    raw_sha256 = compute_sha256(temp_raw_backup)
    dst_conn.close()
    src_conn.close()

    # 3. Gzip Compress
    with open(temp_raw_backup, "rb") as f_in:
        with gzip.open(compressed_backup, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # 4. Remove uncompressed temp copy
    temp_raw_backup.unlink()

    compressed_size_bytes = compressed_backup.stat().st_size
    compressed_sha256 = compute_sha256(compressed_backup)

    manifest_info = {
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "backup_file": compressed_backup.name,
        "backup_path": str(compressed_backup),
        "raw_size_bytes": raw_size_bytes,
        "compressed_size_bytes": compressed_size_bytes,
        "raw_sha256": raw_sha256,
        "compressed_sha256": compressed_sha256,
        "table_counts": table_counts
    }

    # 5. Clean up old backups based on retention policy
    rotate_backups(backup_dir=backup_dir, max_keep=retention_count)

    return manifest_info

def rotate_backups(backup_dir: Path = DEFAULT_BACKUP_DIR, max_keep: int = 7) -> List[str]:
    files = sorted(backup_dir.glob("gpat_backup_*.db.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
    deleted = []
    if len(files) > max_keep:
        for f in files[max_keep:]:
            f.unlink()
            deleted.append(f.name)
    return deleted

def list_backups(backup_dir: Path = DEFAULT_BACKUP_DIR) -> List[Dict[str, Any]]:
    if not backup_dir.exists():
        return []
    files = sorted(backup_dir.glob("gpat_backup_*.db.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
    backups = []
    for f in files:
        backups.append({
            "filename": f.name,
            "path": str(f),
            "size_kb": round(f.stat().st_size / 1024, 2),
            "created_at": datetime.datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()
        })
    return backups

if __name__ == "__main__":
    print(f"Creating SQLite backup of {DEFAULT_DB_PATH}...")
    manifest = create_backup()
    print("Backup completed successfully:")
    print(f"File: {manifest['backup_file']} ({manifest['compressed_size_bytes']} bytes)")
    print(f"SHA-256: {manifest['compressed_sha256']}")
    print(f"Total tables preserved: {len(manifest['table_counts'])}")
    print(f"Questions: {manifest['table_counts'].get('questions', 0)}, Claims: {manifest['table_counts'].get('candidate_claims', 0)}")
