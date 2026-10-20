# GPAT Learning OS (GPAT 2027)

> Offline-first, evidence-grounded AI learning operating system engineered for GPAT 2027 pharmacy aspirants.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.4+-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![SQLite](https://img.shields.io/badge/SQLite-Tri--DB-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org)
[![FSRS](https://img.shields.io/badge/Algorithm-FSRS--4.5-orange.svg)](https://github.com/open-spaced-repetition/fsrs4anki)

---

## 1. Overview & Architecture Highlights

GPAT Learning OS is built to replace bloated test-prep dashboards with a focused, mobile-first mastery engine:
- **Mobile-First UX:** Tailored for quick, thumb-friendly sessions inspired by high-polish consumer apps (Duolingo, Swiggy) with zero decorative fluff.
- **Tri-Database SQLite Architecture:** Strict physical segregation between authoritative baseline content (`data/gpat_baseline.db`), dynamic learner state (`gpat_knowledge.db`), and editorial question review (`data/pyq_topic_staging.db`).
- **Free Spaced Repetition Scheduler (FSRS 4.5):** Scientifically calibrated memory intervals that adapt to student difficulty and retention without penalizing missed days.
- **Syllabus Explorer (3-Tier Drill-Down):** Subject → Unit → Topic progression displaying real verified question counts, high-yield indicators, and concept summaries.
- **Offline Sync & Replay:** Client-side event queuing with idempotent batch push/pull to ensure zero data loss during unstable network conditions.

---

## 2. Repository Layout

```
.
├── backend/                  # FastAPI backend service
│   ├── main.py               # 57 RESTful API endpoints & lifecycle
│   ├── config.py             # App settings, paths, DB connections
│   ├── models/               # Pydantic request/response schemas
│   ├── repositories/         # Database access layer for SQLite
│   ├── services/             # FSRS engine, session orchestrator, sync
│   └── routers/              # Modular API route groups
├── web/                      # Next.js App Router frontend
│   ├── src/app/              # Application pages: /, /today, /study, /pyqs, etc.
│   ├── src/components/       # Reusable UI & card components
│   └── src/lib/              # API clients, offline sync queue, state hooks
├── data/                     # Authoritative data directory
│   ├── gpat_baseline.db      # Frozen baseline content, chunks, & questions
│   └── pyq_topic_staging.db  # Editorial staging database
├── gpat_knowledge.db         # Dynamic learner state & local telemetry DB
├── ontology/                 # GPAT syllabus taxonomy YAML specifications
├── tests/                    # Integration, verification, and E2E test suites
├── reports/                  # Audit and milestone reports
└── docs/                     # Canonical documentation & architectural decisions
```

---

## 3. Quick Start & Development Setup

### Prerequisites
- Python 3.12+ (Python 3.14 recommended)
- Node.js v20+ and npm
- Windows PowerShell or POSIX shell

### 1. Backend Setup
```powershell
# Activate existing virtual environment
.\.venv\Scripts\Activate.ps1

# Verify dependencies & database integrity
python -c "import sqlite3; print(sqlite3.connect('gpat_knowledge.db').execute('PRAGMA integrity_check').fetchone()[0])"

# Start the FastAPI server (runs on http://127.0.0.1:8000)
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup
```powershell
# Navigate to web directory
cd web

# Run production build or dev server
npm run build
npm run dev
# Open http://localhost:3000
```

---

## 4. Canonical Documentation Index

To maintain single-source-of-truth governance, all architectural records and operating procedures are maintained under `docs/`:

- [**`PROJECT_STATUS.md`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/PROJECT_STATUS.md): Current product capabilities, verified features, and known limitations.
- [**`docs/FEATURE_REGISTER.md`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/docs/FEATURE_REGISTER.md): Living feature backlog, implementation tracking, and technical debt.
- [**`docs/ARCHITECTURE.md`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/docs/ARCHITECTURE.md): Database boundaries, data flows, FSRS scheduling, and sync protocol.
- [**`docs/DEVELOPMENT.md`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/docs/DEVELOPMENT.md): Contributor guide, testing commands, PRAGMA checks, and troubleshooting.
- [**`docs/QUALITY_GATES.md`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/docs/QUALITY_GATES.md): Release gates, linting rules, and verification standards.
- [**`docs/DECISIONS.md`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/docs/DECISIONS.md): Architectural Decision Records (ADRs).
- [**`docs/archive/`**](file:///C:/Users/Home/Downloads/PROJECTS/SRE_APP/docs/archive/): Historical phase completion logs and migration summaries.

---

## 5. Automated Verification & Quality Assurance

Run the primary test suites from repository root:

```powershell
# Run core test suites
.\.venv\Scripts\python.exe -m pytest tests/test_production_readiness.py tests/test_phase3_personalized_orchestration.py tests/test_pyq_practice_flow.py -v

# Run Progress & Mission verification
.\.venv\Scripts\python.exe -m pytest tests/verification/test_progress_rewards.py tests/verification/test_daily_mission_flow.py -v

# Run Frontend Typecheck & Build
npm --prefix web run build
```

---

## 6. Safety & Data Integrity Rules

1. **Learner DB Protection:** Never delete or wipe `gpat_knowledge.db`. Tests must run against isolated test databases or verify existing state safely without clearing production learner history.
2. **Ground Truth Content:** Baseline questions in `data/gpat_baseline.db` must have valid syllabus node references. No synthetic question data in production databases.
3. **Deterministic Spaced Repetition:** FSRS weights and interval calculations are deterministic and backed by property-based invariant tests.
