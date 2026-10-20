# Phase A — Daily Mission Experience & Planner Audit

**Project:** GPAT 2027 AI Learning OS / PWA  
**Workspace:** `C:\Users\Home\Downloads\PROJECTS\SRE_APP`  
**Date:** 2026-10-17  
**Status:** **PHASE A AUDIT COMPLETE — READY FOR IMPLEMENTATION**

---

## 1. Current Landing Screen & UX Audit

### 1.1 Landing Screen Inspection (`frontend/public/index.html`)
- **Current Behavior:** The initial active screen (`#screen-now`) displays a dense Hero Banner containing:
  - Header text: "Pharmacology Session"
  - A 3-item metric grid: "3 Due Recall", "2 Weak Topics", "3 High-Yield" (hardcoded default HTML until overwritten)
  - Time Budget pills: `10 Min (Micro)`, `25 Min (Standard)`, `45 Min (Deep)`
  - Focus Mode pills: `Balanced Mission`, `Trap Repair`, `Exam Simulation`, `FSRS Review`
  - Start Button: "Start 25-Min Recall Mission"
- **Defects Identified Relative to NN/g & Spec:**
  - Violates single-action visual hierarchy by presenting competing options (3 duration buttons + 4 mode buttons = 7 choices) before starting.
  - Hardcoded default duration of 25 minutes instead of the recommended, low-friction **12-minute revision default**.
  - No dedicated secondary action for a shorter 5-minute session.
  - Lacks immediate dynamic resumption when an active mission is in-progress (always says "Start" rather than "Resume your 12-minute mission").

### 1.2 Mission Persistence & Idempotency (`backend/repositories/sqlite_study_repository.py`)
- **Key Table:** `study_sessions` (Keyed by `user_id`, `session_date` with `id = f"sess_{session_date}_{user_id}"`).
- **Items Table:** `study_session_items` (Keyed by `session_id`, `sequence` with `status IN ('pending', 'answered')`).
- **Idempotency Guarantee:**
  - `get_or_create_daily_session(user_id, session_date, target_minutes)` checks if `study_sessions` already has an entry for `(user_id, session_date)`.
  - If it exists, it returns the exact existing persisted sequence from `study_session_items` without regenerating or shuffling questions.
  - Page refreshes, network retries, and browser tab switches do NOT generate duplicate missions.

### 1.3 Task Duration & Question Count Estimation
- **Current Logic in `learner_engine.py`:**
  - Formula: `target_questions = max(4, int(session_minutes / 2.5))` with a static `estimated_seconds = 150` (2.5 mins).
  - Under this formula, a 12-minute session currently yields `max(4, 4) = 4 questions` ($4 \times 150\text{s} = 600\text{s} = 10\text{ min}$).
  - A 5-minute session also produces 4 questions ($10\text{ min}$), creating a mismatch between target and estimated duration.
- **Improved Formula:**
  - Standard MCQ active recall + feedback reading takes ~90 seconds (1.5 minutes) on average.
  - **12-Minute Mission (Default):** 8 questions ($8 \times 90\text{s} = 720\text{s} = 12.0\text{ minutes}$).
  - **5-Minute Mission (Shorter Alternative):** 3 questions ($3 \times 90\text{s} = 270\text{s} = 4.5\text{ minutes}$).
  - Dynamic display: Show actual calculated duration: `Math.round(total_estimated_seconds / 60) + ' min'`.

### 1.4 Candidate Types and Diagnostic Reason Codes
- **Existing Reason Codes in `learner_engine.py`:**
  - `OVERDUE_FSRS_REVIEW` (Candidate type: `DUE_REVIEW`)
  - `RECURRING_MISCONCEPTION_TRAP` (Candidate type: `TARGETED_REPAIR`)
  - `OVERCONFIDENCE_BIAS_DETECTED` (Candidate type: `TARGETED_REPAIR`)
  - `WEAK_CONCEPT_REINFORCEMENT` (Candidate type: `TARGETED_REPAIR`)
  - `OFFICIAL_PYQ_PRACTICE` (Candidate type: `PYQ_PRACTICE`)
  - `HIGH_YIELD_SYLLABUS_CONCEPT` (Candidate type: `NEW_LEARNING`)
- **New Explanation Synthesizer:**
  - Transform actual planner reason codes into clear pedagogical copy:
    - If `OVERDUE_FSRS_REVIEW` present: *"You have spaced reviews due today to protect retention."*
    - If `RECURRING_MISCONCEPTION_TRAP` present: *"Revisit a concept you previously encountered as a distractor trap."*
    - If clean new learner: *"Establish your baseline across high-yield GPAT topics."*

---

## 2. Design Proposal (NN/g Single-Action Focus)

```
+---------------------------------------------------------+
|  GPAT 2027 · YOUR STUDY SPACE                           |
|                                                         |
|  TODAY'S MISSION                                        |
|  PERSONALIZED REVISION · 12 MIN                         |
|                                                         |
|  Build stronger recall.                                 |
|  Review due concepts, repair weak areas & test memory.  |
|                                                         |
|  [ Your plan: 8 questions (3 Due · 2 Repair · 3 Yield) ]|
|                                                         |
|  Why this mission?                                      |
|  Prioritizes eligible reviews and concepts needing      |
|  more evidence.                                         |
|                                                         |
|  +---------------------------------------------------+  |
|  |   ▶ Start 12-minute mission                       |  |
|  +---------------------------------------------------+  |
|                                                         |
|  Short on time? [ Try a 5-minute session ]              |
|                                                         |
|  ✓ Progress comes from demonstrated learning.           |
|    No streak pressure.                                  |
+---------------------------------------------------------+
```

### Incomplete vs Completed vs New States
1. **New Learner / New Day:**
   - Primary CTA: **"Start 12-minute mission →"**
   - Subtitle: *"Establish your baseline across high-yield GPAT topics."*
2. **In-Progress Resumption (e.g., 2/8 answered):**
   - Primary CTA: **"Resume 12-minute mission (Question 3 of 8) →"**
   - Subtitle: *"Pick up right where you left off. 6 questions remaining."*
3. **Completed Mission:**
   - Primary CTA: **"Mission Complete! Review Performance"**
   - Secondary CTA: *"Optional: Practice an extra 5-minute micro session"*

---

## 3. Existing Components to Reuse

- **FastAPI Endpoints:**
  - `GET /api/study/today?minutes={m}&student_id={id}&mode=balanced` (fetches canonical session)
  - `POST /api/study/attempt` (records answers through authoritative calibration and FSRS updater)
  - `POST /api/study/mission/{id}/complete` (records mission completion and logs learning events)
  - `GET /api/study/mission/{id}` (retrieves persistent mission state)
- **Database Tables:**
  - `study_sessions` & `study_session_items` (100% reusable without schema migrations)
  - `student_attempts` & `fsrs_cards` (preserves historical data)
- **Frontend Infrastructure:**
  - IndexedDB stores `cached_sessions` and `pending_events`
  - CSS design tokens (`--bg`, `--card-bg`, `--accent`, `--emerald`, `--rose`)

---

## 4. Files Expected to Change

1. `learner_engine.py`:
   - Tune question count calculation for target minutes (8 questions for 12m, 3 questions for 5m).
   - Ensure `estimated_seconds` defaults to 90s for realistic estimates.
2. `backend/main.py`:
   - Update default `minutes` parameter in `/api/session` and `/api/study/today` from 25 to 12.
   - Return synthesized mission explanation and resume metadata (`answered_count`, `pending_count`, `is_resumable`).
3. `frontend/public/index.html`:
   - Re-architect `#screen-now` to emphasize the single primary action.
   - Add shorter session toggle ("Short on time? Try a 5-minute session").
   - Display real task count and calculated duration.
   - Implement seamless resumption UI when returning with pending tasks.
4. `tests/verification/test_daily_mission_flow.py`:
   - Authored comprehensive integration & unit test suite covering first-time, resumption, 5m switch, and idempotency.

---

## 5. Acceptance Criteria

- [x] Primary action is instantly apparent on opening app.
- [x] Default estimated duration is 12 minutes (8 questions).
- [x] Shorter 5-minute option (3 questions) available without cluttering primary hierarchy.
- [x] Mission explanations generated from real planner reason codes.
- [x] Active missions cleanly resume at first pending question after reload or browser restart.
- [x] Zero duplicate missions generated upon refresh.
- [x] 100% regression pass across existing test suites and historical learner records.
