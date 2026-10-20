# Phase 15: Incident Response and Rollback Runbook

**Date:** 2026-10-18  
**Scope:** Controlled Pilot Incident Response, Circuit Breakers, and Rapid Rollback Procedures

---

## 1. Incident Classification Matrix

| Severity | Incident Definition | Trigger Criteria | Immediate Action |
| :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Data integrity loss, cross-user exposure, or security breach | Unauthorized data access, checksum mismatch, or unhandled 5xx error rate $> 5\%$ | Trigger instant pilot halt; isolate database; notify administrator |
| **SEV-2 (High)** | Service degradation or sync failures | p95 latency $> 3\text{s}$ for 10 min, or offline sync failure rate $> 5\%$ | Pause new pilot enrollment; inspect server resource utilization |
| **SEV-3 (Medium)** | Content defect or explanation ambiguity | Reported incorrect answer key or ambiguous distractor rationale | Log feedback in `pilot_feedback`; flag question for SME review |

---

## 2. Emergency Pilot Halt (Circuit Breaker)

To instantly halt external learner access without stopping background processes:

```bash
# Call protected toggle endpoint using the admin secret
curl -X POST "http://127.0.0.1:8000/api/admin/pilot/toggle" \
     -H "Content-Type: application/json" \
     -H "X-Admin-Secret: dev_secret" \
     -d "{\"enabled\": false}"
```

**System Behavior Upon Halt:**
- Real pilot learners (`plt_learner_*`) attempting to fetch sessions or submit attempts will receive `HTTP 503 Service Unavailable ("Pilot access is currently paused or inactive.")`.
- Diagnostic assessment submissions and sync requests fail closed with safe rollbacks.
- Synthetic testing accounts and internal dev accounts retain read access for debugging.

---

## 3. Database Rollback Procedure

If learner records or question baselines experience corruption, execute a non-destructive restoration from the latest verified snapshot:

### Step 1: Identify Latest Clean Backup
```powershell
.venv\Scripts\python -c "from scripts.backup_db import list_backups; print(list_backups())"
```

### Step 2: Verify Backup Integrity & Hash
Every snapshot includes a SHA-256 fingerprint in its accompanying `.meta.json` manifest. The restore utility verifies checksum and `PRAGMA integrity_check` before copying:

```powershell
.venv\Scripts\python scripts/restore_db.py backups/gpat_knowledge_YYYYMMDD_HHMMSS.db.gz
```

### Step 3: Validate Restored State
Confirm protected row counts before resuming traffic:
```powershell
.venv\Scripts\python -c "import sqlite3; c=sqlite3.connect('gpat_knowledge.db'); print('Attempts:', c.execute('select count(*) from student_attempts').fetchone()[0]); print('Cards:', c.execute('select count(*) from fsrs_cards').fetchone()[0]); c.close()"
```

---

## 4. Code & Configuration Rollback Path

If backend changes introduce regressions during the pilot:
1. Revert `backend/main.py` and `backend/pilot_service.py` to the tagged Phase 14 commit:
   ```powershell
   git checkout tags/phase14-release-candidate -- backend/
   ```
2. Rerun the automated test suite to verify stability:
   ```powershell
   .venv\Scripts\pytest tests/ -q
   ```
3. Restart the FastAPI service process.
