# Phase 3 — Preflight Audit & Implementation Plan

**Date:** 2026-10-17  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  
**Databases Audited:**
- Static Baseline: `data/gpat_baseline.db` (229 questions, 221 topics, 6 sources, 505 chunks)
- Runtime Learner: `gpat_knowledge.db` (229 questions, 7 attempts, 11 FSRS cards, 10 events, 3 sessions, 4 misconceptions)

---

## 1. Live System Capability Audit

| Component | Reported Status | Actual Code Inspection Finding | Integration Action for Phase 3 |
|---|---|---|---|
| **FSRS Spaced Scheduler** | Functional | Uses `fsrs` package (`Scheduler`, `Card`, `Rating`, `State`) in `learner_engine.py` | **Preserve & Reuse**. Do not duplicate or rebuild FSRS math. |
| **Calibration & Error Taxonomy** | Implemented | Classifies `SOLID_MASTERY`, `FRAGILE_KNOWLEDGE`, `KNOWLEDGE_GAP`, `OVERCONFIDENT_MISCONCEPTION` | **Preserve & Reuse**. Wire diagnostics into candidate selection reasons. |
| **Study Sessions & Items** | Implemented | `study_sessions` & `study_session_items` in `gpat_knowledge.db` via `SQLiteStudyRepository` | **Extend & Standardize**. Add mission planner versioning, reason codes, and diversity constraints. |
| **Learning Modes** | Implemented | Supports `balanced`, `repair`, `review`, and `exam` in `LearnerEngine.generate_daily_session` | **Refine Candidate Ranker**. Map candidate types (`DUE_REVIEW`, `TARGETED_REPAIR`, `NEW_LEARNING`, `PYQ_PRACTICE`) to existing modes. |
| **Offline Sync Idempotency** | Implemented | `POST /api/sync` uses `synced_client_events` table transactionally | **Preserve & Validate**. Ensure sync updates mission items idempotently. |
| **Baseline vs. Learner DB** | Separated | `data/gpat_baseline.db` is read-only static knowledge; `gpat_knowledge.db` is learner state | **Maintain Strict Rule**. Zero data loss or reset on learner state. |

---

## 2. Identified Deficiencies to Address in Phase 3

1. **Mission Reason Codes:** `study_session_items` previously only recorded `source_type` (`high_yield`, `repair`, `due`). Phase 3 will attach explicit diagnostic reason codes (e.g. `OVERDUE_FSRS_REVIEW`, `RECURRING_MISCONCEPTION_TRAP`, `SYLLABUS_GAP_UNASSESSED`, `HIGH_YIELD_PYQ`).
2. **Diversity Constraints:** When generating sessions, multiple questions from the exact same concept could be consecutively selected. Phase 3 enforces max 2 consecutive questions per concept.
3. **Unassessed Topics Separation:** Topics without student attempts must be marked `UNASSESSED` and not mislabeled as `WEAK`.
4. **Mission API Standardization:** Standardize `/api/study/today`, `/api/study/mission`, `/api/study/mission/{id}/complete`, `/api/study/review-queue` alongside existing `/api/session` and `/api/attempt`.
5. **Synthetic Learner Profiles:** Create automated regression tests with controlled profiles:
   - New Learner (unassessed topics, no false weakness)
   - Overdue Learner (prioritizes FSRS due cards within time budget)
   - High-Confidence Error Learner (prioritizes misconception repair)
   - Low-Confidence Correct Learner (fragile knowledge reinforcement)

---

## 3. File Change Plan

1. `docs/phase3/learner_state_contract.md`: Formalize signals, update rules, and edge cases.
2. `scripts/migrate_phase3_mission_contract.py`: Add `reason_codes`, `estimated_seconds`, `planner_version` to `study_session_items` and `study_sessions`.
3. `learner_engine.py`: Refine `generate_daily_session` with explicit candidate types, diversity constraints, and reason codes.
4. `backend/repositories/sqlite_study_repository.py`: Support new mission fields and review queue retrieval.
5. `backend/main.py`: Add `/api/study/*` endpoints while preserving full backward compatibility with `/api/session`, `/api/attempt`, and `/api/sync`.
6. `tests/test_phase3_personalized_orchestration.py`: End-to-end regression tests across synthetic learner profiles.
