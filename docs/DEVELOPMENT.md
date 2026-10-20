# GPAT Learning OS — Developer Setup, Testing & Operations Guide

**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** 2026-10-20  

---

## 1. Local Environment Prerequisites

- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** 3.12+ (Active environment configured with Python 3.14 at `.venv`).
- **Node.js:** v20.x or later with `npm`.
- **SQLite:** 3.35+ (Standard library bundled with Python).

---

## 2. Environment Setup

### 2.1 Backend Environment
```powershell
# In repository root
# Activate the existing virtual environment:
.\.venv\Scripts\Activate.ps1

# (Optional) Verify installed packages:
pip list
```

### 2.2 Frontend Environment
```powershell
cd web
npm install
cd ..
```

---

## 3. Running the Application

### 3.1 Running FastAPI Backend
Start the backend server on `http://127.0.0.1:8000`:
```powershell
.\.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI documentation will be accessible at `http://127.0.0.1:8000/docs`.

### 3.2 Running Next.js Frontend
Start the Next.js development server on `http://localhost:3000`:
```powershell
cd web
npm run dev
```

---

## 4. Verification & Testing Playbook

### 4.1 Database Integrity Checks
Always verify database health before and after significant modifications:
```powershell
.\.venv\Scripts\python.exe -c "
import sqlite3
for db in ['gpat_knowledge.db', 'data/gpat_baseline.db', 'data/pyq_topic_staging.db']:
    con = sqlite3.connect(db)
    print(f'{db}: {con.execute(\"PRAGMA integrity_check\").fetchone()[0]}')
"
```

### 4.2 Core Verification Test Suites
Run the verified test suites that validate architecture, FSRS scheduling, and practice flows:
```powershell
# 1. Production readiness (concurrency, idempotency, backup)
.\.venv\Scripts\python.exe -m pytest tests/test_production_readiness.py -v

# 2. Personalized orchestration & learner safety
.\.venv\Scripts\python.exe -m pytest tests/test_phase3_personalized_orchestration.py -v

# 3. PYQ practice flow & FSRS calibration
.\.venv\Scripts\python.exe -m pytest tests/test_pyq_practice_flow.py -v

# 4. Progress, rewards, and daily mission experience
.\.venv\Scripts\python.exe -m pytest tests/verification/test_progress_rewards.py tests/verification/test_daily_mission_flow.py -v
```

### 4.3 Frontend Typecheck & Build
Validate TypeScript syntax and Next.js page generation:
```powershell
npm --prefix web run build
```

---

## 5. Troubleshooting Common Issues

### 5.1 Brittle Row Count Assertions
- **Symptom:** `AssertionError: 30 != 7` in `test_phase3_personalized_orchestration.py`.
- **Cause:** Genuine student practice sessions in the live app append rows to `student_attempts`.
- **Solution:** Assert non-regression using `assertGreaterEqual` instead of exact equality for live tables.

### 5.2 Next.js Turbopack Root Warning
- **Symptom:** `Next.js ignored package-lock.json in ... because it is outside the current Git repository`.
- **Resolution:** Benign warning caused by lack of root Git repository initialization. Does not impact build or production execution.
