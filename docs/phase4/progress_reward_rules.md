# Progress Reward Rules Specification
**GPAT 2027 Learning OS | Phase 4 Feature 4**  
**Document Version:** 1.0.0  
**Status:** APPROVED & FROZEN

---

## 1. Core Principles & Ethical Boundaries

1. **Demonstrated Learning Over Engagement:**
   - Achievements are awarded strictly upon verified cognitive accomplishments, not for opening the app, scrolling, or clicking repeatedly.
2. **Deterministic & Explainable:**
   - Every rule is evaluated deterministically in Python using SQL-committed evidence. No probabilistic language models or non-deterministic heuristics are permitted in eligibility decisions.
3. **Non-Punitive Persistence:**
   - Earned achievements are permanent. Missing days, taking a break, or pausing a weekly goal never resets or revokes earned achievements.
4. **Idempotent & Replay-Safe:**
   - Duplicate submissions (such as replayed offline sync batches) never produce duplicate awards.
5. **No Streak Pressure:**
   - No streak resets to zero, no loss threats, and no notifications demanding daily participation.

---

## 2. Formal Reward Eligibility Rules

### Rule A: Meaningful Mission Completion (`MISSION_COMPLETION`)
- **Eligibility Criteria:**
  1. The study session exists in `study_sessions` with `status = 'completed'` and `user_id = student_id`.
  2. The count of items in `study_session_items` with `status = 'answered'` equals the count of total items in that session ($\text{answered} = \text{total} > 0$).
  3. The completion event has not already been processed for this `session_id`.
- **Evidence Reference:**
  - `evidence_type`: `session_id`
  - `evidence_id`: e.g. `sess_2026-10-17_student_01`
  - `evidence_metadata`: `{"questions_count": 8, "session_date": "2026-10-17", "target_minutes": 12}`
- **Display Metadata:**
  - `title`: "Mission Accomplished"
  - `description`: "Completed all personalized retrieval tasks in today's mission."

---

### Rule B: Verified Delayed Recall Improvement (`DELAYED_RECALL`)
- **Eligibility Criteria:**
  1. An attempt is submitted where `is_correct = 1` for `question_id`.
  2. At least one previous attempt on the same `question_id` exists for this student.
  3. The time difference between the current attempt and the most recent previous attempt is $\ge 24\text{ hours}$ ($86,400\text{ seconds}$).
  4. Immediate repetitions ($< 24\text{ hours}$) are strictly excluded.
- **Evidence Reference:**
  - `evidence_type`: `question_id`
  - `evidence_id`: e.g. `q_gpat_001`
  - `evidence_metadata`: `{"interval_hours": 36.5, "prior_attempt_date": "2026-10-15T10:00:00Z"}`
- **Display Metadata:**
  - `title`: "Durable Recall Milestone"
  - `description`: "Successfully recalled concept after a 24+ hour retention interval."

---

### Rule C: Misconception Correction (`MISCONCEPTION_REPAIR`)
- **Eligibility Criteria:**
  1. A student previously had an active record in `student_misconceptions` with `status IN ('ACTIVE', 'RECURRING')` for `concept_id`.
  2. The student submits a correct answer (`is_correct = 1`) on a subsequent question testing that `concept_id`.
  3. The misconception record transitions to `status = 'REPAIRED'` and `resolved_at IS NOT NULL`.
  4. Only one award per repaired concept instance to prevent repetitive farming.
- **Evidence Reference:**
  - `evidence_type`: `concept_id`
  - `evidence_id`: e.g. `ans_alpha_blockers`
  - `evidence_metadata`: `{"concept_name": "Alpha-Adrenergic Antagonists", "distractor_reason": "Postural hypotension trap", "resolved_at": "2026-10-17T02:00:00Z"}`
- **Display Metadata:**
  - `title`: "Conceptual Trap Repaired"
  - `description`: "Successfully untangled a recurring misconception through active retrieval."

---

### Rule D: Demonstrated Topic Mastery (`TOPIC_MASTERY`)
- **Eligibility Criteria:**
  1. The concept in `concept_memory_state` satisfies the deterministic mastery classifier:
     - `attempts >= 3`
     - `(correct / attempts) >= 0.80` (80%+ accuracy)
     - `stability >= 7.0` (FSRS stability at least 7 days)
     - `misconception_count == 0` (or all previously caught traps repaired)
  2. The concept transitions to `DEMONSTRATED_MASTERY`.
- **Evidence Reference:**
  - `evidence_type`: `concept_id`
  - `evidence_id`: e.g. `pk_absorption`
  - `evidence_metadata`: `{"concept_name": "Drug Absorption", "attempts": 4, "accuracy": 1.0, "stability_days": 8.5}`
- **Display Metadata:**
  - `title`: "Demonstrated Topic Mastery"
  - `description`: "Consolidated robust memory stability and high accuracy across multiple sessions."

---

### Rule E: Personal Best Milestone (`PERSONAL_BEST`)
- **Eligibility Criteria:**
  1. A completed study session or mock exam contains at least 5 questions.
  2. The accuracy achieved in this session is strictly higher than any previously completed session for this learner.
  3. Window comparison evaluates all completed sessions prior to the current session.
- **Evidence Reference:**
  - `evidence_type`: `session_id`
  - `evidence_id`: e.g. `sess_2026-10-17_student_01`
  - `evidence_metadata`: `{"previous_best_accuracy": 75.0, "current_accuracy": 100.0, "question_count": 8}`
- **Display Metadata:**
  - `title`: "Personal Best Accuracy"
  - `description`: "Achieved your highest retrieval accuracy across a full study mission."

---

### Rule F: Flexible Weekly Study Goal (`WEEKLY_GOAL_MET`)
- **Eligibility Criteria:**
  1. The learner has an active weekly goal in `learner_goals` with `status = 'active'` (default target: 5 missions/week).
  2. The count of completed missions in the current ISO week (Monday 00:00:00 UTC to Sunday 23:59:59 UTC) meets or exceeds `target_count`.
  3. Evaluated once per ISO week string (e.g. `2026-W42`).
  4. If a goal is missed, no penalty, streak wipe, or negative badge is ever created.
- **Evidence Reference:**
  - `evidence_type`: `iso_week`
  - `evidence_id`: e.g. `2026-W42`
  - `evidence_metadata`: `{"target_count": 5, "completed_count": 5, "iso_week": "2026-W42"}`
- **Display Metadata:**
  - `title`: "Weekly Study Goal Met"
  - `description`: "Reached your weekly planned study missions with consistent practice."
