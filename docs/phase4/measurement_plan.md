# Phase 4 Telemetry & Outcome Measurement Plan

**GPAT 2027 AI Learning OS / PWA**  
**Core Metric:** Verified Delayed Learning Gain per Minute Studied ($\Delta \text{Recall} / \text{Time}$).  
**Status:** Approved for Gate 1 Baseline & Experimentation.

---

## 1. Principles of Educational Telemetry

Unlike commercial social platforms that maximize screen time, session length, and daily active user (DAU) stickiness through anxiety-inducing mechanics, this application measures **retention efficiency**, **conceptual recovery**, and **exam readiness**.

### Non-Negotiable Privacy and Telemetry Rules:
1. **No Unnecessary Tracking:** No continuous cursor tracking, eye tracking, keystroke dynamics, or cross-site analytics.
2. **Stable Deterministic Identifiers:** All events record stable `client_event_id` or `event_id`, timestamps in ISO 8601 UTC, and explicit entity keys (`user_id`, `question_id`, `concept_id`, `session_id`).
3. **Transparent Utility:** Every logged event directly powers spaced repetition scheduling (FSRS), misconception trap identification, or offline synchronization reconciliation.

---

## 2. Learning Telemetry Taxonomy

The system emits events directly into the relational `learning_events` table in `gpat_knowledge.db`:

| Event Type | Trigger Point | Critical Payload Attributes |
|---|---|---|
| `SESSION_STARTED` | Learner launches daily study mission | `session_id`, `session_date`, `target_minutes`, `mode`, `question_count` |
| `QUESTION_ANSWERED` | Answer submitted and evaluated | `selected_option`, `is_correct`, `response_time_sec`, `confidence`, `calibration_category`, `error_type`, `fsrs_rating`, `stability_days` |
| `MISCONCEPTION_DETECTED` | Incorrect distractor selected | `distractor_reason`, `error_type`, `calibration` (e.g. `OVERCONFIDENT_MISCONCEPTION`) |
| `MISSION_COMPLETED` | Final question in session answered | `mission_id`, `completed_at`, `accuracy_percent`, `tasks_completed`, `repairs_completed`, `fsrs_advanced` |
| `OFFLINE_SYNC_QUEUED` | Client answers in offline mode | `client_event_id`, `question_id`, `selected_option`, `confidence`, `timestamp` |
| `OFFLINE_SYNC_ANSWERED` | Offline attempts synced to backend | `client_event_id`, `timestamp`, `is_correct`, `idempotent_status` |

---

## 3. Mathematical Metric Definitions

### 3.1 Mission Completion Rate ($MCR$)
$$\text{MCR} = \frac{\sum \text{Completed Study Sessions}}{\sum \text{Started Study Sessions}} \times 100$$
- **Goal:** $>85\%$.
- **Diagnostic Signal:** If $<70\%$, mission task count or duration is causing cognitive overload or session fatigue.

### 3.2 Delayed Recall Retention Rate ($DRR_{14}$)
$$\text{DRR}_{14} = \frac{\text{Correct First-Try Reviews with Scheduled Interval } \ge 14 \text{ days}}{\text{Total Due Reviews with Scheduled Interval } \ge 14 \text{ days}} \times 100$$
- **Goal:** $\ge 80\%$.
- **Diagnostic Signal:** Measures durable memory retention independent of short-term cramming.

### 3.3 Misconception Repair Half-Life ($T_{1/2}$)
The median number of study sessions required for an active conceptual trap to transition from `ACTIVE`/`RECURRING` to `REPAIRED` via successful targeted retrieval.
- **Goal:** $\le 2$ sessions.
- **Diagnostic Signal:** Validates that diagnostic explanations and active recall cues resolve underlying confusion rather than producing repeated failures.

### 3.4 Time-to-Mastery Efficiency ($TME$)
$$\text{TME} = \frac{\text{Cumulative Active Retrieval Minutes to reach DEMONSTRATED\_MASTERY}}{\text{Count of Mastered Syllabus Topics}}$$
- **Goal:** $<15$ minutes per concept.
- **Diagnostic Signal:** Evaluates whether retrieval-practice prompts effectively consolidate knowledge without busywork.

### 3.5 Post-Lapse Return Rate ($PLRR$)
$$\text{PLRR} = \frac{\text{Learners who return within 72 hours of an unstudied day}}{\text{Total Learners experiencing an unstudied day}} \times 100$$
- **Goal:** $>75\%$.
- **Diagnostic Signal:** Verifies absence of streak anxiety or demotivation after life interruptions.

### 3.6 Question Challenge & Flag Rate ($QFR$)
$$\text{QFR} = \frac{\text{Questions flagged or challenged by learners}}{\text{Total Question Presentations}} \times 100$$
- **Goal:** $<1.0\%$.
- **Diagnostic Signal:** Immediate warning for questions with ambiguous stems, miskeyed answers, or outdated pharmaceutical guidelines.

---

## 4. Current Empirical Baseline Measurement

Measured from the production learner database (`gpat_knowledge.db`) and baseline database (`data/gpat_baseline.db`):

| Measurement Dimension | Baseline Value | Evidence Status |
|---|---|---|
| **Total Study Sessions** | 3 sessions (32 total items) | Persisted in `study_sessions` |
| **Historical Attempts Recorded** | 7 attempts | Persisted in `student_attempts` |
| **Baseline Attempt Accuracy** | 57.1% | Verified from historical attempts |
| **Mean Response Time** | 12.91 seconds | Verified from historical attempts |
| **Mean Calibration Confidence** | 4.14 / 5.0 | High baseline confidence |
| **Active FSRS Memory Cards** | 11 cards | Mean stability: 528.32 days; Mean difficulty: 3.38 |
| **Active Concept Memory States** | 14 assessed concepts | 24 concepts unassessed |
| **Published Baseline MCQs** | 229 verified MCQs | 100% published in `gpat_baseline.db` |
| **Quarantined Items** | 3 MCQs | Held in `pyq_review_queue` (ambiguous/diagram dependent) |

---

## 5. Controlled Evaluation & Experimentation Protocol

When testing new experience variants (e.g., Mastery Map visual matrix vs. flat list):
1. **Never alter historical learner rows in `gpat_knowledge.db`**.
2. **Run parallel evaluations using synthetic learner personas** on cloned SQLite fixtures.
3. **A/B Testing Constraints:** Only test pedagogical parameters (e.g. mission length, cue presentation format); never vary correctness or official answer key truth.
4. **Statistical Rigor:** Report insufficient sample size as *exploratory* rather than asserting causal significance.
