# GPAT Learning OS — Baseline Repository & System Audit Report

**Date:** 2026-10-20  
**Environment:** Windows PowerShell, Python 3.14 (`.venv`), Node.js v20+, Next.js 16.4.2 (Turbopack)  
**Project Root:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  
**Audit Purpose:** Comprehensive governance baseline before document consolidation and artifact archiving.

---

## 1. Executive Summary

GPAT Learning OS is an offline-capable, evidence-grounded AI learning system tailored for GPAT 2027 pharmacy aspirants. The system combines:
1. A **Next.js App Router** frontend (`web/`) with 8 main routes (`/`, `/today`, `/study`, `/pyqs`, `/review`, `/mocks`, `/progress`, `/settings`).
2. A **FastAPI** backend (`backend/main.py`) exposing 57 RESTful endpoints for session orchestration, FSRS spaced repetition, mock exams, rewards, and sync.
3. A **tri-database SQLite architecture** enforcing clear boundaries between authoritative content ontology, dynamic learner state, and editorial staging.

All 3 SQLite databases pass `PRAGMA integrity_check` cleanly. TypeScript validation passes across the frontend, and core backend verification test suites pass completely.

---

## 2. Repository Inventory & File Distribution

| Top-Level Directory | File Count | Purpose / Status |
| :--- | :--- | :--- |
| `.venv/` | 48,742 | Isolated Python 3.14 virtual environment (dependencies). |
| `web/` | 36,289 | Next.js App Router frontend (includes `node_modules` and `.next`). |
| `reports/` | 240 | Historical phase logs, audit summaries, and design reviews. |
| `BASELINE docs/` | 222 | Raw GPAT syllabus brochures, PDFs, markdown extractions, and manifests. |
| `scripts/` | 129 | Data extraction, verification, database seeding, and benchmark scripts. |
| `tests/` | 74 | Integration, verification, evaluation, and end-to-end tests. |
| `backend/` | 42 | FastAPI app, service layer, repositories, schemas, models. |
| `data/` | 8 | SQLite content & staging DBs, embeddings, taxonomy exports. |
| `docs/` | 19 | Existing architecture and design documents. |
| `ontology/` | 2 | GPAT syllabus taxonomy YAML definitions (`gpat_ontology.yaml`). |

---

## 3. Database Architecture & Health Check

### 3.1 SQLite Database Status
- **`gpat_knowledge.db` (Root):**
  - **Integrity:** `ok`
  - **Tables:** 44 (including `fsrs_cards`, `student_attempts`, `study_sessions`, `study_session_items`, `learning_events`, `user_achievements`, `sync_queue`, `pilot_configs`).
  - **Purpose:** Authoritative dynamic learner state and local telemetry.
  - **Safety Policy:** Strictly append/update; never purged or dropped during builds.
- **`data/gpat_baseline.db`:**
  - **Integrity:** `ok`
  - **Tables:** 27 (including `syllabus_nodes`, `content_blocks`, `block_embeddings`, `gpat_questions`, `pyqs`).
  - **Purpose:** Authoritative frozen content, chunk embeddings, and verified syllabus taxonomy.
  - **Question Inventory:** 2,063 baseline questions; all questions have verified syllabus mapping.
- **`data/pyq_topic_staging.db`:**
  - **Integrity:** `ok`
  - **Tables:** 2 (`staged_pyqs`, `editorial_reviews`).
  - **Purpose:** Staging area for editorial review of questions before promotion to baseline.

---

## 4. Backend Endpoints (57 Total)

Audited directly from `backend/main.py`. Grouped by functional capability:

1. **System & Health (4):**
   - `GET /api/health`
   - `GET /health`
   - `GET /api/v1/health`
   - `GET /api/pilot/health`
2. **Personalized Study & Today Flow (11):**
   - `GET /api/study/today`
   - `POST /api/study/start`
   - `POST /api/study/submit-item`
   - `POST /api/study/finish`
   - `POST /api/study/item/evaluate`
   - `GET /api/study/session/{session_id}`
   - `POST /api/study/session/{session_id}/complete`
   - `GET /api/study/session/{session_id}/status`
   - `POST /api/study/sync`
   - `GET /api/study/mission/today`
   - `POST /api/study/mission/switch`
3. **Question Player & Practice (6):**
   - `GET /api/practice/questions`
   - `POST /api/practice/attempt`
   - `GET /api/practice/question/{question_id}`
   - `GET /api/practice/question/{question_id}/explanation`
   - `GET /api/practice/explanation/{question_id}`
   - `GET /api/practice/question/{question_id}/notes`
4. **PYQ Explorer & Taxonomy (8):**
   - `GET /api/pyqs/years`
   - `GET /api/pyqs/subjects`
   - `GET /api/pyqs/search`
   - `GET /api/pyqs/by-year/{year}`
   - `GET /api/pyqs/by-subject/{subject}`
   - `GET /api/pyqs/topic-distribution`
   - `GET /api/pyqs/inventory-summary`
   - `GET /api/taxonomy/tree`
5. **FSRS Spaced Repetition Review (5):**
   - `GET /api/fsrs/due`
   - `POST /api/fsrs/review`
   - `GET /api/fsrs/card/{card_id}`
   - `GET /api/fsrs/stats`
   - `POST /api/fsrs/reschedule`
6. **Mock Exams & Blueprints (6):**
   - `GET /api/mocks/blueprints`
   - `POST /api/mocks/generate`
   - `GET /api/mocks/{mock_id}`
   - `POST /api/mocks/{mock_id}/submit`
   - `GET /api/mocks/{mock_id}/results`
   - `GET /api/mocks/history`
7. **Progress, Analytics & Rewards (7):**
   - `GET /api/progress/summary`
   - `GET /api/progress/syllabus-coverage`
   - `GET /api/progress/mastery-by-subject`
   - `GET /api/progress/activity-heatmap`
   - `GET /api/rewards/achievements`
   - `GET /api/rewards/coins-balance`
   - `POST /api/rewards/claim`
8. **Synchronization & Offline Replay (4):**
   - `POST /api/sync/push`
   - `GET /api/sync/pull`
   - `GET /api/sync/status`
   - `POST /api/sync/conflict-resolve`
9. **Pilot Administration & Backup (6):**
   - `GET /api/admin/pilot/metrics`
   - `POST /api/admin/pilot/export`
   - `POST /api/admin/pilot/flag`
   - `POST /api/admin/backup/create`
   - `POST /api/admin/backup/restore`
   - `GET /api/admin/backup/history`

---

## 5. Frontend Routes & Components

Verified via `npm --prefix web run build`:
- `GET /` — Root dashboard / landing redirect.
- `GET /today` — Mobile-first daily study hub (Today hero, exam horizon, mission CTA, focus cards, quick review).
- `GET /study` — Syllabus Explorer (3-tier progressive drill-down: Subject → Unit → Topic detail).
- `GET /pyqs` — PYQ Practice quiz mode (single-question focus, instant answer evaluation, filter drawer).
- `GET /review` — FSRS spaced repetition review queue.
- `GET /mocks` — Official 125-question mock exams & mini-mocks.
- `GET /progress` — 5-screen Progress & Rewards center (Overview, Journey, Activity, Mastery, Rewards).
- `GET /settings` — Sync configuration, exam target date, and pilot preferences.

**Build Result:** Next.js 16.4.2 compiled cleanly in 7.3s; TypeScript finished in 7.9s with 0 errors across 11 static/dynamic pages.

---

## 6. Verification Status & Test Suite Health

| Test Suite | Result | Details |
| :--- | :--- | :--- |
| `tests/test_production_readiness.py` | 8/8 PASSED | Container entrypoint, backup/restore, concurrency, sync idempotency. |
| `tests/test_pyq_practice_flow.py` | 4/4 PASSED | PYQ inventory, staging provenance, rich fields, FSRS calibration. |
| `tests/test_phase3_personalized_orchestration.py` | 5/5 PASSED | Synthetic personas, unassessed separation, diversity, learner DB safety. |
| `tests/verification/test_progress_rewards.py` | 7/7 PASSED | Empty states, achievements, delayed recall, 24h intervals, mastery classifier. |
| `tests/verification/test_daily_mission_flow.py` | 6/6 PASSED | First-time learner mission, 5m switch, resumption, evidence headlines. |

---

## 7. Technical Debt & Archival Actions

1. **Test Suite Hygiene:**
   - Isolated tests should not assume fixed row counts in `gpat_knowledge.db` because genuine user interaction increases `student_attempts`. Fixed in `test_phase3_personalized_orchestration.py`.
2. **Documentation Sprawl:**
   - Root directory contains numerous milestone reports (`PHASE2_ARCHITECTURE.md`, `phase3a_summary.md`, etc.).
   - Canonical single-source-of-truth documents must now govern the system: `README.md`, `PROJECT_STATUS.md`, `docs/FEATURE_REGISTER.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/QUALITY_GATES.md`, `docs/DECISIONS.md`.
   - Historical phase logs are being indexed and linked into `docs/archive/` without data loss.
