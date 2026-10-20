# Phase 6.5: Database Rollback & Recovery Procedure

**Date:** 2026-10-18  
**Scope:** `data/gpat_baseline.db` and `gpat_knowledge.db`  

---

## 1. Automated Snapshot Verification

Online SQLite snapshots are created with SHA-256 validation before every staging or migration operation:

```powershell
.venv\Scripts\python.exe scripts/gate0_baseline_audit.py
```

Latest Verified Checksums:
- `data/gpat_baseline.db`: `74fab7f1024c2fc06445f51f0d363fdd27675ad127f91c9d2e0041052c2f1464`
- `gpat_knowledge.db`: `d3adb285a40975eebc07ec9cf6ff4a27cc92cfeb74b701abc5d000d3d1c279cc`

---

## 2. Fast Rollback Procedure (Emergency Restore)

If database corruption or unwanted migrations occur during testing:

### Step 1: Terminate active server processes
Ensure no active SQLite locks are held:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Step 2: Restore from verified backup
```powershell
Copy-Item backups/gpat_baseline_20261018_004441.db data/gpat_baseline.db -Force
Copy-Item backups/gpat_knowledge_20261018_004441.db gpat_knowledge.db -Force
```

### Step 3: Verify restored state
```powershell
.venv\Scripts\python.exe -c "
import sqlite3
for db in ['data/gpat_baseline.db', 'gpat_knowledge.db']:
    conn = sqlite3.connect(db)
    print(db, 'Integrity:', conn.execute('PRAGMA integrity_check').fetchall())
    print(db, 'FK Violations:', len(conn.execute('PRAGMA foreign_key_check').fetchall()))
    conn.close()
"
```

---

## 3. Staged Mapping Rollback Procedure

If the 137 staged topic mappings are promoted to production and later need reversal:

```powershell
.venv\Scripts\python.exe -c "
import sqlite3
conn = sqlite3.connect('data/gpat_baseline.db')
cur = conn.cursor()
st_conn = sqlite3.connect('data/pyq_topic_staging.db')
st_cur = st_conn.cursor()
st_cur.execute('SELECT question_id, current_topic_id FROM staged_topic_mappings')
rows = st_cur.fetchall()
for qid, orig_tid in rows:
    cur.execute('UPDATE baseline_questions SET topic_id = ? WHERE id = ?', (orig_tid, qid))
conn.commit()
print('Reversed', len(rows), 'mappings to original current_topic_id.')
conn.close()
st_conn.close()
"
```
