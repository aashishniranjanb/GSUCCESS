# Phase 15: Telemetry & Event Schema Specification

**Date:** 2026-10-18  
**Scope:** Event logging, deduplication, privacy controls, and data retention

---

## 1. Principles of Data Minimization & Privacy

1. **Zero PII Collection:**
   - No names, physical addresses, email addresses, phone numbers, or IP addresses are stored in event payloads.
2. **Pseudonymous Identifiers:**
   - Real learners use IDs matching `plt_learner_[a-f0-9]{8}`.
   - Synthetic automated tests use IDs matching `syn_learner_[a-f0-9]{8}` or `test_*`.
3. **Deduplication & Idempotency:**
   - Offline batch sync events are deduplicated using client-generated UUIDs (`client_event_id`) with unique index constraints in `synced_client_events`.
   - Repeated event submissions return HTTP 200 with status `"duplicate"` without double-counting attempt statistics.

---

## 2. Telemetry Event Catalog

All telemetry is recorded in the `learning_events` table with the following schema:

```sql
CREATE TABLE learning_events (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    question_id TEXT,
    concept_id TEXT,
    timestamp TIMESTAMP NOT NULL,
    payload_json TEXT
);
```

### Event Specifications

| Event Type | Trigger | Key Payload Fields | Usage |
| :--- | :--- | :--- | :--- |
| `SESSION_STARTED` | Learner launches Daily Mission | `session_id`, `session_date`, `target_minutes`, `mode`, `question_count` | Engagement & session cadence tracking |
| `QUESTION_ANSWERED` | Learner submits question response | `selected_option`, `is_correct`, `response_time_sec`, `confidence`, `calibration_category`, `error_type`, `fsrs_rating`, `stability_days` | Learning retention, FSRS scheduling, calibration curve |
| `MISCONCEPTION_DETECTED` | Learner selects common distractor | `distractor_reason`, `error_type`, `calibration` | Diagnostic repair queue generation |
| `OFFLINE_SYNC_ANSWERED` | Offline answer batch replayed | `client_event_id`, `timestamp`, `is_correct` | Offline reliability & sync fidelity |
| `MOCK_EXAM_EVALUATED` | Diagnostic or full mock scored | `exam_id`, `blueprint_name`, `score`, `accuracy`, `percentile` | Assessment score trajectories |
| `EXPLANATION_FEEDBACK` | Learner submits explanation review | `feedback_type`, `rating`, `comment` | Content quality & explanation tuning |

---

## 3. Feedback Event Schema (`pilot_feedback`)

```sql
CREATE TABLE pilot_feedback (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    question_id TEXT,
    feedback_type TEXT NOT NULL, -- EXPLANATION_CLARITY, DISTRACTOR_ACCURACY, OCR_ERROR, APP_BUG
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    submitted_at TIMESTAMP NOT NULL
);
```

---

## 4. Retention, Access Controls & Deletion Policy

1. **Access Controls:**
   - Direct database access is restricted to the local host filesystem.
   - Telemetry exports via `/api/admin/pilot/metrics` require authenticated administrative credentials (`X-Admin-Secret`).
2. **Data Retention:**
   - Pilot telemetry is retained for 90 days following pilot completion.
   - Upon completion of analysis, individual attempt logs may be purged while retaining aggregate score distributions.
3. **Learner Deletion Protocol:**
   - Any participant requesting withdrawal can have their learner record and associated attempt logs purged via administrative deletion script:
     ```sql
     DELETE FROM student_attempts WHERE student_id = ?;
     DELETE FROM learning_events WHERE user_id = ?;
     DELETE FROM pilot_learners WHERE student_id = ?;
     DELETE FROM pilot_feedback WHERE student_id = ?;
     ```
