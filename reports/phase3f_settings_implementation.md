# GPAT Learning OS — Phase 3F: Settings, Account & Learner Preferences Implementation Report

**Date:** 2026-10-19  
**Scope:** Phase 3F — Account Management, Authoritative Study Goals, Client Preferences, and Architecture Transparency  
**Status:** Verification Passed (Exit 0 across all quality gates)  

---

## 1. Executive Summary

Phase 3F implements the Settings, Account & Learner Preferences workspace in the Next.js App Router frontend, backed by the FastAPI backend and SQLite `learner_goals` table in `gpat_knowledge.db`.
- **Account & Identity Transparency:** Displays pseudonymous learner identity (`student_01`) with verified SQLite data isolation. Notes Supabase Auth as the designated authentication provider for VPS deployment, without exposing access secrets or fake session tokens.
- **Authoritative Study Cadence:** Connects weekly study goal configuration to backend `learner_goals` via `POST /api/rewards/goal` and `GET /api/rewards`. Allows learners to configure non-punitive weekly targets (3, 5, 7, 10, 14 missions/week) with server-side persistence.
- **Client Learning Preferences:** Implements local preference persistence for preferred daily mission duration (8m–20m), FSRS review batch size (5–25 Qs), and reduced-motion mode via `localStorage`.
- **Honest Notification Status:** Acknowledges that background Web Push notifications require active VPS subscription workers and explicitly marks push reminders as not yet implemented rather than fabricating alerts.
- **Architecture & Data Safety:** Displays verified database paths, PWA caching mechanisms, and automated SQLite backup status.

---

## 2. API Contract & Persistence Architecture

### A. Endpoints Integrated
1. `GET /api/rewards?student_id=student_01`:
   - Retrieves active weekly study goal (`target_count`, `achieved_count`, `is_met`, `week_range`, `iso_week`) and milestone awards.
2. `POST /api/rewards/goal`:
   - Updates `target_count` in `learner_goals` table with transactional idempotency (`UNIQUE(student_id, goal_type)`).
   - Validates `target_count` $\in [1, 20]$ with default 5 missions/week.

### B. Client Preferences Storage
- Key: `gpat_learning_os_preferences`
- Stored attributes:
  - `preferredMissionDurationMinutes` (default: 12)
  - `preferredReviewBatchSize` (default: 10)
  - `reducedMotion` (default: false)
  - `theme` ("dark")
  - `notificationsEnabled` (false)
  - `reminderTime` (null)

---

## 3. Frontend Components Implemented

| Component / File | Path | Description |
|---|---|---|
| **API Client** | `web/src/lib/api/settings.ts` | Typed `fetchLearnerRewards` and `updateWeeklyGoal` methods. |
| **Preferences Helper** | `web/src/lib/preferences.ts` | Local storage wrapper for client-side display and session preferences. |
| **API Types** | `web/src/lib/api/types.ts` | Added `WeeklyStudyGoal`, `LearnerRewardsResponse`, and `LearnerLocalPreferences`. |
| **Settings Workspace** | `web/src/components/settings/settings-workspace.tsx` | Account details, authoritative goal updater, session preference selectors, notification status, and database safety transparency. |
| **Page Controller** | `web/src/app/settings/page.tsx` | Next.js controller with skeleton loading and error retry recovery. |

---

## 4. Integrity and Safety Guarantees

1. **Zero Database Corruption:** `learner_goals` rows are created or updated safely; zero mutations against `questions`, `student_attempts`, or `fsrs_cards`.
2. **Preservation of Raw Rows:** `student_attempts` (7), `fsrs_cards` (11), and `questions` (2063) verified intact.
3. **No Credential Exposure:** Neither service keys nor fake tokens are exposed in client code.
