# GPAT Learning OS — Living Feature Register & Technical Debt

**Version:** 1.0.0  
**Status:** Active  
**Last Audit:** 2026-10-20  

This register tracks all primary features, enhancements, and known technical debt items using stable identifiers.

---

## 1. Feature Register

| Feature ID | Category | Feature Name | Description | Status | Verification Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TODAY-101** | Study Hub | Daily Hero & Streak | Displays greeting, day streak, and earned coins from real attempts. | **Verified** | `tests/verification/test_daily_mission_flow.py` |
| **TODAY-102** | Study Hub | Exam Horizon | Target countdown card for GPAT 2027. | **Verified** | Frontend Next.js build |
| **TODAY-103** | Study Hub | Daily Mission CTA | 12-min adaptive session or switchable 5-min micro session. | **Verified** | `test_03_short_5min_mission_selection` |
| **TODAY-104** | Study Hub | Personalized Focus | Highlights topics needing urgent review based on FSRS stability. | **Verified** | `tests/test_phase3_personalized_orchestration.py` |
| **STUDY-201** | Syllabus | 3-Tier Progressive Drill | Subject → Unit → Topic progressive disclosure navigation. | **Verified** | Next.js App Router `/study` |
| **STUDY-202** | Syllabus | High-Yield Topic Filtering | Filter topics marked high-yield with question count chips. | **Verified** | `data/gpat_baseline.db` syllabus nodes |
| **STUDY-203** | Syllabus | Topic Detail Screen | Integrated view of Learn, Practice PYQs, and Notes. | **Verified** | `tests/test_pyq_practice_flow.py` |
| **PYQ-301** | Practice | Single-Question Quiz | Distraction-free quiz UI with 1 question at a time. | **Verified** | Next.js App Router `/pyqs` |
| **PYQ-302** | Practice | Instant Answer Feedback | Correctness animation & shake effect on incorrect choices. | **Verified** | `test_pyq_practice_flow.py` |
| **PYQ-303** | Practice | Filter Drawer | Filter by Subject, Exam Year, and Difficulty. | **Verified** | Backend `/api/pyqs/search` |
| **FSRS-401** | Spaced Rep | FSRS 4.5 Scheduler | Card intervals adjusted using FSRS algorithm weights. | **Verified** | `test_04_isolated_attempt_fsrs_and_calibration` |
| **FSRS-402** | Spaced Rep | Spaced Review Queue | `/review` queue rendering cards due today. | **Verified** | Backend `/api/fsrs/due` |
| **PROG-501** | Progress | 5-Screen Journey | Overview, Syllabus Journey, Activity, Mastery, Rewards. | **Verified** | `tests/verification/test_progress_rewards.py` |
| **PROG-502** | Progress | Honest Empty State | Clean initial zero-state for new students without mock data. | **Verified** | `test_01_honest_empty_state_for_new_learner` |
| **PROG-503** | Progress | Coin & Reward System | Accrues coins on study milestones, redeemable for rewards. | **Verified** | `tests/verification/test_progress_rewards.py` |
| **MOCK-601** | Mock Exam | Official 125 Mock | Timed 180m, 125 questions mapped to GPAT blueprint. | **Verified** | `tests/evaluation/test_mock_engine.py` |
| **MOCK-602** | Mock Exam | Scoring & Penalty Engine | +4 for correct, -1 for incorrect, 0 for unattempted. | **Verified** | `backend/services/mock_service.py` |
| **SYNC-701** | Offline Sync | Local Event Queue | Stores attempts and reviews in SQLite `sync_queue`. | **Verified** | `test_sync_idempotency_replay` |
| **SYNC-702** | Offline Sync | Idempotent Push/Pull | Safely replays queued learner events without duplicate records. | **Verified** | `test_07_offline_sync_evaluates_achievements` |

---

## 2. Technical Debt Register

| Debt ID | Subsystem | Issue / Description | Severity | Remediation Plan |
| :--- | :--- | :--- | :--- | :--- |
| **DEBT-01** | Version Control | Root directory is not currently initialized as a git repo. | Medium | Initialize git or define explicit upstream mirror workflow. |
| **DEBT-02** | Test Hygiene | Fixed row count assertions in tests against active learner DB. | Low | Resolved in `test_phase3_personalized_orchestration.py:139` via `assertGreaterEqual`. |
| **DEBT-03** | Sync Architecture | Multi-device concurrent write conflict resolution lacks 3-way merge. | Low | Currently idempotent replay; add version-vector conflict handler in Phase 4 sync upgrade. |
| **DEBT-04** | Documentation | Over 100 historical milestone reports in root and `reports/`. | Medium | Consolidated into canonical docs; historical files cataloged in `docs/archive/`. |
| **DEBT-05** | Frontend Turbopack | Warning regarding root `package-lock.json` outside Next.js root. | Low | Configure `turbopack.root` in `web/next.config.ts` if needed. |
