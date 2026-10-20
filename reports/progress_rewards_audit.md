# Gate 0 Audit: Learning-Based Progress Rewards System
**Project:** GPAT 2027 Learning OS | Phase 4 Feature 4  
**Date:** 2026-10-17  
**Status:** AUDIT COMPLETE — CONTRACTS FROZEN

---

## 1. Executive Summary & Verification Findings

This audit analyzes the existing architecture of the GPAT 2027 Learning OS to prepare for the implementation of **Feature 4: Learning-Based Progress Rewards**.

In accordance with Phase 4 Engagement Principles and the Measurement Plan:
- **No Extrinsic Gamification / No Variable Loot / No Streak Freezes:** The system completely avoids streak resets, red warning banners, public leaderboards, artificial urgency, or rewards for simple clickthrough/idle time.
- **Evidence-Grounded Learning Milestones:** Rewards recognize verifiable, demonstrated cognitive accomplishments:
  1. *Meaningful Mission Completion* (All required tasks answered in a persisted session).
  2. *Verified Delayed Recall Improvement* (Correct retrieval after a defined $\ge 24\text{h}$ or $\ge 14\text{d}$ interval on an FSRS card).
  3. *Misconception Correction* (Targeted resolution of an `ACTIVE`/`RECURRING` trap).
  4. *Demonstrated Topic Mastery* (Authoritative deterministic transition to `DEMONSTRATED_MASTERY`).
  5. *Personal Bests* (Highest delayed recall accuracy or lowest error rate over comparable windows).
  6. *Flexible Non-Punitive Weekly Study Goals* (Configurable targets that can be paused or edited without penalty).

---

## 2. Answers to Audit Checklist Questions

### 1. How missions are created and marked complete
- **Creation:** Initiated via `/api/study/today` or `LearnerEngine.generate_daily_session(...)`. Persisted to `study_sessions` with `status = 'active'`, `target_minutes`, and items in `study_session_items` with `status = 'pending'`.
- **Completion:** `/api/study/mission/{id}/complete` updates `study_sessions.status = 'completed'` and `completed_at = now_iso`. Emits a `MISSION_COMPLETED` event into `learning_events`.
- **Policy Enforcement:** Mission completion must require that all items in `study_session_items` for that session have `status = 'answered'`. If shortening occurred before starting (e.g. 5m mission), completion is evaluated against the 3 generated items, not the 8 of a 12m mission.

### 2. Which events are authoritative for a completed answer
- Both synchronous attempt submission via `/api/attempt` (and `/api/study/attempt`) and offline sync via `/api/sync` insert an attempt into `student_attempts`.
- Synchronous calls log `QUESTION_ANSWERED` (and optionally `MISCONCEPTION_DETECTED`).
- Offline synchronization logs `OFFLINE_SYNC_ANSWERED` and records the client ID in `synced_client_events`.
- Authoritative evidence source: committed records in `student_attempts`, `fsrs_cards`, and `student_misconceptions`.

### 3. Whether mission completion is already idempotent
- In `backend/main.py`:
  ```python
  @app.post("/api/study/mission/{mission_id}/complete")
  def complete_study_mission(mission_id: str, repo: StudyRepository = Depends(get_repo)):
      # Updates study_sessions SET status = 'completed', completed_at = ? WHERE id = ?
      # Then logs MISSION_COMPLETED
  ```
- Calling `/complete` multiple times updates the existing completed record. However, without a dedicated check, it would log multiple `MISSION_COMPLETED` events. The achievement engine must enforce idempotency so that duplicate `/complete` calls do not trigger duplicate achievement awards.

### 4. How delayed recall can be distinguished from immediate repetition
- Distinguishing Criteria:
  - **Immediate Repetition:** Multiple attempts on the same question or concept within the same study session or within $< 1$ hour.
  - **Delayed Recall:** Correct retrieval of a concept/card where:
    - An earlier attempt exists ($\ge 24\text{ hours}$ earlier, or card `due` scheduled $\ge 1$ day in the past and `last_review` was $\ge 24\text{ hours}$ ago).
    - FSRS card stability has advanced, or retention is tested across different calendar dates.
- Immediate retries within seconds/minutes will be excluded from delayed recall awards.

### 5. How misconceptions are represented and resolved
- **Table:** `student_misconceptions`.
- **Status Lifecycle:** `ACTIVE` (1st detection) $\rightarrow$ `RECURRING` ($\ge 2\text{ detections}$) $\rightarrow$ `REPAIRED` (student answers correctly on a subsequent attempt).
- **Authoritative Transition:** In `LearnerEngine.record_attempt`:
  ```python
  if is_correct:
      cur.execute("""
      UPDATE student_misconceptions
      SET status = 'REPAIRED', resolved_at = ?
      WHERE student_id = ? AND concept_id = ? AND status IN ('ACTIVE', 'RECURRING')
      """, (now_iso, student_id, concept_id))
  ```
- **Reward Guard:** An achievement is awarded only if a misconception record previously existed in `ACTIVE` or `RECURRING` state and transitioned to `REPAIRED` via a verified correct attempt. Repeated attempts on the same question cannot farm awards.

### 6. How mastery states are calculated
- **Deterministic Classifier** in `backend/main.py` (`/api/progress`):
  - `UNASSESSED`: `attempts == 0`
  - `NEEDS_REPAIR`: `misconception_count > 0`
  - `DEMONSTRATED_MASTERY`: `attempts >= 3` AND `(correct / attempts) >= 0.8` AND `stability >= 7.0 days`
  - `RETAINING`: `stability >= 3.0 days` AND `(correct / attempts) >= 0.6`
  - `LEARNING`: In-progress (`attempts < 3` or `stability < 3.0 days`)
- **Reward Guard:** The achievement engine directly reuses this exact logic. Zero competing or secondary thresholds are introduced.

### 7. Whether achievement-related tables or UI already exist
- **Audit Result:** No achievement tables exist currently in `gpat_knowledge.db` (verified via `sqlite_master` query).
- **UI:** The Progress screen (`screen-progress`) currently contains tabs for "Memory & Mastery", "Mock Exams", and "AI System Quality". No achievement or rewards feed currently exists.

### 8. How dates and time zones are handled
- All timestamps in SQLite and API payloads use ISO 8601 UTC (`datetime.datetime.now(timezone.utc).isoformat()`).
- Session grouping uses UTC calendar date (`YYYY-MM-DD`).
- Weekly goals will define week boundaries as ISO week (Monday 00:00:00 UTC to Sunday 23:59:59 UTC) or configurable user timezone, with default Monday 00:00:00 UTC.

### 9. Whether offline events can be replayed
- Yes, `/api/sync` accepts batches of offline attempts with `client_event_id`.
- Uniqueness is strictly protected via `synced_client_events (client_event_id PRIMARY KEY)`. Replays are marked `"status": "duplicate"` and ignored.
- The achievement engine will be called during `/api/sync` processing and will inherit this transactional idempotency.

### 10. How tests isolate their learner database from production data
- All verification tests use `tempfile.NamedTemporaryFile` and copy `gpat_knowledge.db` into a temporary file.
- `os.environ["GPAT_DB_PATH"] = str(tmp_db)` redirects all database queries to the cloned fixture.
- Canonical baseline records in `gpat_knowledge.db` (7 attempts, 11 FSRS cards, 10 events, 3 sessions, 3 synced events) are strictly asserted and preserved.

---

## 3. Proposed Data Model

To preserve the clean separation between immutable syllabus/baseline content and mutable learner state, two lightweight tables will be introduced to `gpat_knowledge.db`:

### 3.1 `learner_achievements` Table
Stores authoritative, deduplicated milestones awarded to learners.
```sql
CREATE TABLE IF NOT EXISTS learner_achievements (
    id TEXT PRIMARY KEY,                       -- e.g. ach_student_01_MISSION_COMPLETED_sess_2026-10-17_student_01
    student_id TEXT NOT NULL,
    achievement_type TEXT NOT NULL,            -- MISSION_STREAK_FREE, DELAYED_RECALL_MILESTONE, MISCONCEPTION_REPAIR, TOPIC_MASTERY, PERSONAL_BEST, WEEKLY_GOAL_MET
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    evidence_type TEXT NOT NULL,               -- session_id, concept_id, question_id, weekly_window
    evidence_id TEXT NOT NULL,                 -- e.g. sess_2026-10-17_student_01 or ans_alpha_blockers
    evidence_metadata_json TEXT,               -- Details (e.g. interval_days, stability, accuracy)
    awarded_at TEXT NOT NULL,
    rule_version TEXT NOT NULL DEFAULT '1.0.0',
    UNIQUE(student_id, achievement_type, evidence_id)
);
```
- **Deduplication Guarantee:** The `UNIQUE(student_id, achievement_type, evidence_id)` constraint prevents farming or duplicate awards even if an event is replayed or processed concurrently.

### 3.2 `learner_goals` Table
Stores user-configurable, non-punitive study targets.
```sql
CREATE TABLE IF NOT EXISTS learner_goals (
    id TEXT PRIMARY KEY,                       -- e.g. goal_student_01_weekly
    student_id TEXT NOT NULL,
    goal_type TEXT NOT NULL,                   -- 'completed_missions', 'completed_reviews'
    target_count INTEGER NOT NULL DEFAULT 5,   -- e.g. 5 missions per week
    status TEXT NOT NULL DEFAULT 'active',     -- 'active', 'paused'
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(student_id, goal_type)
);
```

---

## 4. Event Contracts & Achievement Types

| Achievement Type | Qualifying Event / Condition | Evidence Captured |
|---|---|---|
| `MISSION_COMPLETION` | Session has `status = 'completed'` and all items answered. | `evidence_id = session_id`, `evidence_metadata = {questions_count, accuracy}` |
| `DELAYED_RECALL` | Correct attempt on question where prior attempt occurred $\ge 24\text{ hours}$ ago. | `evidence_id = question_id`, `evidence_metadata = {prior_attempt_time, interval_hours, stability}` |
| `MISCONCEPTION_REPAIR` | Incorrect trap resolved to `REPAIRED` via subsequent verified correct attempt. | `evidence_id = concept_id`, `evidence_metadata = {concept_name, distractor_reason, resolved_at}` |
| `TOPIC_MASTERY` | Concept transitions to `DEMONSTRATED_MASTERY` (3+ attempts, 80%+ acc, stability 7d+). | `evidence_id = concept_id`, `evidence_metadata = {attempts, accuracy, stability_days}` |
| `PERSONAL_BEST` | Personal highest session accuracy (min 5 questions) or lowest error rate. | `evidence_id = window_id`, `evidence_metadata = {previous_best, current_best}` |
| `WEEKLY_GOAL_MET` | Weekly completed missions $\ge \text{target_count}$ within current ISO week. | `evidence_id = iso_week_string (e.g. 2026-W42)`, `evidence_metadata = {target, achieved}` |

---

## 5. Risks & Mitigation Plan

1. **Risk: Offline Replay Duplicate Badges:**
   - *Mitigation:* `learner_achievements` enforces `UNIQUE(student_id, achievement_type, evidence_id)`. Replaying `/api/sync` results in `INSERT OR IGNORE` and 0 duplicate rows.
2. **Risk: False Learning Claims:**
   - *Mitigation:* The system explicitly defines what is measured (e.g. "Verified 24h Recall Check", "Misconception Resolved") and never makes unsubstantiated claims that a badge proves permanent retention.
3. **Risk: Compulsive / Streak Pressure:**
   - *Mitigation:* Zero streak counters, zero daily punishment, zero lost achievements. Weekly goals can be paused or edited without resetting past progress.
4. **Risk: Production DB Corruption:**
   - *Mitigation:* Canonical database `gpat_knowledge.db` is backed up before migration; all tests run strictly against `NamedTemporaryFile` fixtures.

---

## 6. Acceptance Criteria

- [x] Audit complete and contracts frozen (Gate 0).
- [ ] Lightweight data models created with strict unique constraints (Gate 2).
- [ ] Deterministic `AchievementService` created with zero LLM dependence (Gate 3).
- [ ] Restrained, non-intrusive UI added to the Progress screen with honest empty states (Gate 4).
- [ ] Configurable weekly goal endpoint (`/api/rewards/goal`) implemented (Gate 5).
- [ ] Offline sync and replay safety verified with zero duplicate awards (Gate 6).
- [ ] 20+ automated unit, integration, and property tests passing (Gate 7).
- [ ] Zero loss of the 7 historical attempts, 11 FSRS cards, 10 events, 3 sessions in `gpat_knowledge.db`.
