# GPAT Learning OS — Frontend Rollback Runbook

**Date:** 2026-10-18  
**Scope:** Immediate Reversion Procedure from Next.js (`web/`) to Legacy Vanilla PWA (`frontend/public/`)  
**Target Project:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`

---

## 1. Principles of Rollback Safety

1. **Physical Isolation:** The new Next.js application resides in `web/` and never touches or modifies the existing `frontend/public/` directory.
2. **FastAPI Default Serving:** FastAPI (`backend/main.py`) mounts `frontend/public/` at `/` by default. Even when developing `web/`, the legacy PWA remains fully functional on the FastAPI port.
3. **Zero Database Overwrites:** Reverting the frontend requires zero database restoration or schema rollback because all database operations are governed by FastAPI and SQLite.

---

## 2. Emergency Rollback Triggers

Initiate immediate rollback if any of the following occur:
- Critical rendering regression blocking the Daily Mission on mobile devices (e.g. Redmi Note 11).
- Unhandled JavaScript exception loops causing mobile battery drain or PWA crash.
- Broken local IndexedDB event replay resulting in un-synced learner attempts.
- Navigation or accessibility failure preventing screen reader interaction.

---

## 3. Step-by-Step Rollback Execution

### Step 1: Terminate the Next.js Development Server
If the Next.js process is active:
```powershell
# Stop any running node process serving web/
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Step 2: Verify Legacy PWA Assets
Ensure that the original vanilla PWA files in `frontend/public/` are unmodified:
```powershell
Test-Path frontend/public/index.html
Test-Path frontend/public/sw.js
Test-Path frontend/public/manifest.json
```

### Step 3: Start / Verify the FastAPI Legacy Host
Run the backend server directly:
```powershell
.venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Navigate in browser to:
`http://localhost:8000`

The legacy PWA will immediately load from `frontend/public/index.html`.

### Step 4: Clear Client Cache & Unregister Service Worker (If Necessary)
If a pilot client registered an experimental Service Worker from `web/`:
1. In Chrome / Edge DevTools: **Application** -> **Service Workers** -> **Unregister**.
2. **Storage** -> **Clear site data**.
3. Reload `http://localhost:8000`. The legacy service worker (`gpat-ai-v1`) will activate cleanly.

### Step 5: Validate Database Safety
Verify that learner attempts and integrity remain intact:
```powershell
.venv\Scripts\python -c "
import sqlite3
for db in ['gpat_knowledge.db', 'data/gpat_baseline.db', 'data/pyq_topic_staging.db']:
    con = sqlite3.connect(db)
    print(db, con.execute('PRAGMA integrity_check').fetchall())
    con.close()
"
```

---

## 4. Rollback Verification Checklist

- [ ] FastAPI backend responds with `200 OK` at `http://localhost:8000/api/health`.
- [ ] Legacy PWA loads at `http://localhost:8000/`.
- [ ] Daily Mission and PYQ practice loops operate normally in legacy PWA.
- [ ] No learner records were lost or corrupted.
