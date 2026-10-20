# GPAT Learning OS — Requirement-to-Code Specification Audit

**Document Date:** 2026-10-19  
**Specification:** [`BEST_GPAT_UX.md`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/BEST_GPAT_UX.md)  
**Evaluated Codebase:** Next.js App Router (`web/`), FastAPI (`backend/`), SQLite Databases (`gpat_knowledge.db`, `data/gpat_baseline.db`)  
**Current Phase Audited:** Phase 5A (Living Daily Home UI)

---

## 1. Executive Audit Summary

A comprehensive requirement-to-code audit was conducted against `BEST_GPAT_UX.md`. The product vision defines a personal study guide combining:
1. A guided daily journey with optional direct access to any feature.
2. A structured syllabus workspace.
3. One reusable question player.
4. Custom unit checks and covered-syllabus mini mocks.
5. Spaced repetition using the existing FSRS engine.
6. Honest, evidence-based progress.
7. Offline study and safe synchronization.

Every requirement was classified into one of four verified states:
- **Verified:** Implementation inspected and supporting test/build evidence confirmed.
- **Partial:** Basic implementation exists, but core specification capabilities remain incomplete.
- **Missing:** Not yet implemented in code or UI.
- **Blocked:** Requires an unavailable API, unconfirmed data contract, or external dependency.

---

## 2. Detailed Requirement-to-Code Matrix

| Section / Capability | Requirement Description | Relevant File / API | Status | Evidence / Verified Behavior | Identified Gap & Risk | Recommended Next Action |
|---|---|---|---|---|---|---|
| **6.1 Today Screen** | Target-date countdown | `web/src/components/today/exam-countdown-card.tsx` | **VERIFIED** | Configured by default to 2027-02-02; timezone-safe UTC calculation; inline popover editor; handles past/invalid dates honestly. | Official GPAT 2027 date unconfirmed by NBEMS; correctly labeled as learner target. | Maintain configurable target in settings. |
| **6.1 Today Screen** | Two recommended topic choices | `web/src/components/today/two-study-choices-section.tsx`, `GET /api/study/today` | **VERIFIED** | Shows Option A (Pharmacology) and Option B (Pharmaceutics); estimated 12 min; grounds recommendation in real FSRS due status and curriculum weightage. | If backend session fails, fallback presents syllabus link. | Connect multi-subject dynamic candidate generation. |
| **6.1 Today Screen** | Start study session | `web/src/app/today/page.tsx`, `POST /api/study/attempt` | **VERIFIED** | Launches interactive `QuestionCard` loop directly in-page; submits to `/api/study/attempt`; records FSRS updates and learning events. | Completing sets marks session completed. Resumption verified locally. | Unify into reusable question player in Phase 5C. |
| **6.1 Today Screen** | Studied Today vs Plan Next | `web/src/components/today/unified-study-plan-today.tsx` | **VERIFIED** | Segmented controller. Studied tab shows real SQLite learning events; Plan next tab maintains durable local queue without mutating DB history. | Planning changes currently stored in `localStorage` (`gpat_learner_study_plan_v1`), not synced server-side. | Safe local draft meets Phase 5A gate. |
| **6.1 Today Screen** | FSRS Review summary | `web/src/components/today/fsrs-review-summary-card.tsx`, `GET /api/study/review-queue` | **VERIFIED** | Real-time due cards displayed with violet flashcard visual tokens and direct link to `/review`. | Handles loading and empty states cleanly. | Retain authoritative FSRS connection. |
| **6.1 Today Screen** | Subject explorer preview | `web/src/components/today/syllabus-explorer-preview.tsx`, `GET /api/syllabus/tree` | **VERIFIED** | 5 colorful domain pills (Pharmacology, Pharmaceutics, Chem, Pharmacognosy, Biotech) with live topic counts from baseline DB. | Links into `/study` with query filter. | Standardize subject colors across all pages. |
| **6.2 Syllabus Explorer** | Subject → Unit → Topic → Learning Objective hierarchy | `web/src/app/study/page.tsx`, `GET /api/syllabus/tree` | **PARTIAL** | Displays hierarchical tree of 5 exam subjects, 19 academic courses, and 221 topics. Search by keyword works. | Does not yet filter by learner state (studied, not assessed, needs repair, provisional mastery). Resource links not visually separated by type. | **Phase 5B Priority:** Enhance Study Explorer with topic mastery states and deep resource links. |
| **6.3 Topic Workspace** | Deep topic overview (Objectives, References, Flashcards, Practice) | `web/src/components/study/topic-detail-panel.tsx`, `GET /api/syllabus/topic/{id}` | **PARTIAL** | Shows Reference chunks, Level 5 objectives, Bloom's levels, and flashcards. | Does not provide direct "Test this topic" launcher or "Take unit check" action. Recent performance per topic is missing. | Implement dedicated topic study & assessment workspace in Phase 5B. |
| **6.4 Reusable Question Player** | Single universal question player for Daily Mission, Topic Practice, PYQs, and Mocks | `web/src/components/study/question-card.tsx` | **PARTIAL** | Operates Daily Mission in `/today`. Has timer, option selection, submit, instant feedback, and rationale. | Not shared with `/pyqs` (which has custom code) or `/mocks`. Lacks confidence rating scale (1-5), bookmarking, and mistake review mode. | **Phase 5C Priority:** Consolidate into universal question session player. |
| **6.5 PYQs Practice** | Historical question bank with year/subject filters | `web/src/app/pyqs/page.tsx`, `GET /api/pyqs/practice` | **VERIFIED** | Filter by year (2020-2026), paper, and subject; displays answer provenance and verification status. | Uses separate card UI instead of the shared player; bookmarking state is local-only. | Wire to universal question player in Phase 5C. |
| **6.6 Spaced Repetition Review** | Active recall with FSRS ratings (Again, Hard, Good, Easy) | `web/src/app/review/page.tsx`, `GET /api/study/review-queue`, `POST /api/study/review-rating` | **VERIFIED** | Flashcard flip interaction; rating submission updates FSRS stability and difficulty; write-lock collision resolved in Phase 4. | Does not distinguish between overdue vs due today vs learning cards in UI tabs. | Enhance review filtering in Phase 5E. |
| **6.7 Mini Mock Builder** | Unit checks, custom mini mocks, and full simulations | `web/src/app/mocks/page.tsx`, `backend/evaluation.py` | **PARTIAL** | Standard blueprints (`sprint_25`, `diagnostic_50`, `full_125`) exist in backend and can be started/submitted. | Custom "Build My Mock" (selecting specific studied units and custom question counts) is missing in frontend UI. | **Phase 5D Priority:** Build dedicated Mini Mock Builder with unit selection and distribution preview. |
| **6.8 Learning Progress** | Four separate measures: coverage, accuracy, retention, exam readiness | `web/src/app/progress/page.tsx`, `GET /api/progress` | **PARTIAL** | Summary displays overall accuracy, active study days, and FSRS workload. | Retention and Exam readiness are not explicitly separated from practice accuracy. Lacks "insufficient data" fallback state. | Refactor progress analytics to enforce the four distinct indicators in Phase 5E. |
| **6.9 Settings & Account** | Target exam date, study cadence, data export, and session info | `web/src/app/settings/page.tsx`, `web/src/components/settings/settings-workspace.tsx` | **VERIFIED** | Allows configuring target date, mission duration (8-20m), review batch size, and weekly mission goals backed by SQLite. | Supabase Auth remains in local pilot mode with pseudonymous session ID (`student_01`). | Keep stable until Phase 5F. |
| **10. Accessibility** | WCAG 2.2 AA (44px touch targets, visible focus, reduced motion, contrast) | `web/src/app/globals.css`, component styles | **VERIFIED** | Minimum 44px touch targets; visible 2px focus ring; `.animate-sway` and `.animate-enter` disabled under `prefers-reduced-motion`. | Screen reader aria-labels present on icon buttons. | Continue verifying across all pages. |
| **15. Offline / PWA** | Service worker caching, IndexedDB queue, and safe sync | `backend/main.py` (`POST /api/sync`), `web/public/sw.js` | **PARTIAL** | Backend idempotent sync endpoint (`synced_client_events`) tested and verified. UI shows offline banner. | Client-side IndexedDB background auto-sync worker needs visual queue status indicators. | Verify and harden in Phase 5F. |

---

## 3. Independent Verification Results (Phase 5A)

1. **ESLint Static Analysis:**  
   `npm run lint` — **0 errors, 0 warnings** across all files in `web/`.
2. **Strict TypeScript Compilation:**  
   `npx tsc --noEmit` — **Exit code 0**. Zero type errors across the entire Next.js project.
3. **Next.js Production Build:**  
   `npm run build` — **Exit code 0**. All 11 App Router static and dynamic pages compiled successfully in 2.4s.
4. **Live HTTP Server Check:**  
   `GET http://localhost:3000/today` returned **HTTP 200** with complete HTML and CSS assets.
5. **Backend Automated Regression:**  
   `pytest tests/test_production_readiness.py tests/test_backup_recovery.py tests/test_pyq_practice_flow.py` — **14 passed in 37.59s**.
6. **Database Integrity & Content Lock:**  
   - `PRAGMA integrity_check` returned `ok` for both `gpat_knowledge.db` and `data/gpat_baseline.db`.
   - Baseline questions count: exactly **2,063** verified.
   - Learner baseline records verified unaltered: `attempts=7, cards=11, events=10, sessions=3, goals=1, achievements=4`.

---

## 4. Architectural Findings & Dependency Analysis

1. **The Question Accessibility Problem:**  
   The question bank contains 2,063 baseline questions across 5 exam subjects. Currently, questions can only be accessed via:
   - Daily Mission on `/today` (authoritative 8-question focus loop).
   - PYQ list on `/pyqs` (year-based filter list).
   - Topic detail on `/study` (static list inside the TopicDetailPanel).
   - Mock session on `/mocks` (predefined blueprints).
2. **Why Students Feel Lost:**  
   The syllabus has 221 topics. If a student wants to study a specific unit (e.g. *Physical Pharmaceutics: Rheology & Micromeritics*), they cannot currently launch a focused 10-question practice session directly from that topic. Furthermore, when they want to test their readiness across the 3 units they have completed, they are forced to either take a full 125-question mock (which covers topics they haven't touched) or browse an unorganized question list.
3. **Dependency Sequencing:**  
   - *Phase 5B (Syllabus Explorer)* is necessary so students can navigate and locate topics, but navigation alone does not allow them to answer questions.
   - *Phase 5C (Reusable Question Player)* is the foundational engine. Building custom mini mocks (Phase 5D) before having a unified question player would cause severe code duplication between mock exams, topic practice, and daily missions.
   - Therefore, the recommended progression is:  
     **Phase 5B (Syllabus Explorer & Topic Workspace)** &rarr; **Phase 5C (Reusable Question Session Player)** &rarr; **Phase 5D (Mini Mock Builder)**.
