import sqlite3
import hashlib
import json
import gzip
import os
import shutil
from datetime import datetime

os.makedirs("backups", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_file(src_path, dst_tag):
    if not os.path.exists(src_path):
        return None
    backup_path = f"backups/{dst_tag}_{timestamp}.db"
    # Backup using sqlite online backup API
    with sqlite3.connect(src_path) as s, sqlite3.connect(backup_path) as d:
        s.backup(d)
    
    # Calculate sha256
    h = hashlib.sha256()
    with open(backup_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    sha = h.hexdigest()
    sz = os.path.getsize(backup_path)
    return {"path": backup_path, "sha256": sha, "size_bytes": sz}

base_bk = backup_file("data/gpat_baseline.db", "gpat_baseline")
learn_bk = backup_file("gpat_knowledge.db", "gpat_knowledge")

print("Backup Baseline DB:", base_bk)
print("Backup Learner DB:", learn_bk)

def audit_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Integrity check
    cur.execute("PRAGMA integrity_check")
    integ = cur.fetchall()
    
    # FK check
    cur.execute("PRAGMA foreign_key_check")
    fk = cur.fetchall()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    counts = {}
    for t in tables:
        cur.execute(f"SELECT count(*) FROM [{t}]")
        counts[t] = cur.fetchone()[0]
        
    conn.close()
    return {"integrity": integ, "foreign_key_violations": fk, "counts": counts}

res_base = audit_db("data/gpat_baseline.db")
res_learn = audit_db("gpat_knowledge.db")

print("\n--- BASELINE DB CHECKS ---")
print("Integrity:", res_base["integrity"])
print("FK Violations:", len(res_base["foreign_key_violations"]))
for t, c in sorted(res_base["counts"].items()):
    print(f"  {t:30s}: {c}")

print("\n--- LEARNER DB CHECKS ---")
print("Integrity:", res_learn["integrity"])
print("FK Violations:", len(res_learn["foreign_key_violations"]))
for t, c in sorted(res_learn["counts"].items()):
    print(f"  {t:30s}: {c}")

# Protected learner tables checksums
def get_table_checksum(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM [{table_name}] ORDER BY ROWID")
    rows = cur.fetchall()
    conn.close()
    raw = json.dumps(rows, default=str, sort_keys=True)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest(), len(rows)

print("\n--- PROTECTED LEARNER STATE FINGERPRINTS ---")
for tbl in ["student_attempts", "fsrs_cards", "learning_events", "study_sessions", "study_session_items", "synced_client_events", "learner_achievements", "learner_goals"]:
    sha, cnt = get_table_checksum("gpat_knowledge.db", tbl)
    print(f"  {tbl:25s}: count={cnt:4d} | sha256={sha}")
