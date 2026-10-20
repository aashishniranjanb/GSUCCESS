# Phase 3 — Learner-State Contract & Signal Specification

**Version:** 3.0.0  
**Effective Date:** 2026-10-17  
**Authority:** GPAT 2027 Learning OS Engine  

---

## 1. Principles of Learner State

1. **Deterministic Calculation:** All learner state calculations are reproducible from recorded attempts, FSRS cards, and learning events.
2. **Never Equate Unassessed with Weak:** Topics with 0 attempts are classified as `UNASSESSED`. Only topics with verified failure evidence (accuracy < 50% or recurring misconceptions) are classified as `WEAK`.
3. **Delayed Retrieval Requirement:** Mastery is not awarded for a single immediate correct answer. Stable mastery (`SOLID_MASTERY`) requires delayed retrieval evidenced by FSRS stability $\ge 3.0$ days or repeated correct attempts spaced over multiple sessions.
4. **Diagnostic Value of Confidence:** Confidence is captured on a 1–5 scale:
   - High Confidence ($\ge 4$) + Incorrect $\implies$ `OVERCONFIDENT_MISCONCEPTION` (immediate repair priority).
   - Low Confidence ($< 4$) + Correct $\implies$ `FRAGILE_KNOWLEDGE` (retrieval reinforcement).
   - High Confidence ($\ge 4$) + Correct $\implies$ `SOLID_MASTERY` (extended spacing interval).
   - Low Confidence ($< 4$) + Incorrect $\implies$ `KNOWLEDGE_GAP` (instructional guidance).

---

## 2. Core Learner-State Signals

| Signal | Source | Calculation | Planning Effect |
|---|---|---|---|
| **`REVIEW_URGENCY`** | `fsrs_cards` | `due <= CURRENT_TIMESTAMP`, scaled by overdue hours | High priority candidate selection for review slots |
| **`MISCONCEPTION_RISK`** | `student_misconceptions` | Active trap count ($\times 2.5$) + overconfidence count ($\times 1.8$) | Triggers targeted repair mode and diagnostic questions |
| **`CONCEPT_MASTERY`** | `concept_memory_state` | Correct attempts / Total attempts with retrievability decay | Weak concepts receive $2.0\times$ priority weighting |
| **`TOPIC_ASSESSMENT_STATE`** | `student_attempts` | `attempts == 0 ? UNASSESSED : (acc < 0.5 ? WEAK : MASTERED)` | Distinguishes new learning from remediation |
| **`EXAM_IMPORTANCE`** | `concepts.importance_score` | Normalized syllabus weight (1 to 10) | Multiplies baseline priority for high-yield topics |

---

## 3. Mission Planner Schema Contract

Each daily mission is persisted in `study_sessions` with associated tasks in `study_session_items`:

```json
{
  "mission_id": "sess_2026-10-17_student_01",
  "planner_version": "phase3-v1",
  "user_id": "student_01",
  "session_date": "2026-10-17",
  "time_budget_minutes": 25,
  "status": "active",
  "tasks": [
    {
      "task_id": "item_sess_2026-10-17_student_01_01",
      "question_id": "pyq_gpat_2026_001",
      "concept_id": "pk_absorption",
      "candidate_type": "DUE_REVIEW",
      "reason_codes": ["OVERDUE_FSRS_REVIEW"],
      "estimated_minutes": 2.5,
      "status": "pending"
    }
  ]
}
```

---

## 4. Diversity & Anti-Repetition Constraints

1. **Max Consecutive Concept Tasks:** No more than 2 consecutive tasks in a single mission may share the same `concept_id`.
2. **Same-Session Idempotency:** A question already answered correctly in the active mission cannot be scheduled again in the same mission.
3. **Session Duration Bounds:** Target questions $N = \max(4, \lfloor\text{minutes} / 2.5\rfloor)$.
