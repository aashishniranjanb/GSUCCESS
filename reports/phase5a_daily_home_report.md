# GPAT Learning OS — Phase 5A: Living Daily Home Experience Report

**Document Date:** 2026-10-19  
**Status:** IMPLEMENTATION COMPLETE & VERIFIED  
**Primary Route:** `/today`  
**Frontend Stack:** Next.js App Router (`web/`), TypeScript, Tailwind CSS v4, Phosphor Icons  
**Visual Style:** Botanical dark navy foundation with domain-coded organic illustrations, fluid progress, and uncluttered cards

---

## 1. Living UI/UX Transformation

The Daily Home screen (`/today`) has been upgraded from a dark monochrome layout into a lively, premium study-planning experience inspired by the approved art-direction reference:

1. **Dark Botanical Navy Foundation:**
   - Canvas surface upgraded to `#080B12` with raised cards at `#0E1320` and elevated surfaces at `#151C2E`.
   - Subtle analog organic grain overlay preserved for surface depth.
   - Added gentle organic animations: `.animate-sway` (swaying leaf stems) and `.animate-pulse-soft` (glowing synaptic knowledge spores), strictly disabled when `prefers-reduced-motion` is active.
2. **Hero Banner Artwork (`BotanicalHeroGraphic`):**
   - Features an original inline SVG artwork showcasing an aspirant with open pharmacopeias color-coded by discipline: **Pharmacology** (Green), **Pharmaceutics** (Sky Blue), and **Biochemistry** (Amber).
   - Accented by flowing leaves, gentle floating knowledge spores, and chemical receptor rings.
   - Friendly, encouraging greeting: *"Today, let's make progress. Choose a focus, build your plan, and keep moving towards your GPAT 2027 goal."*
3. **Exam Countdown (2 February 2027 Target):**
   - Initialized by default to **2 February 2027** as the learner's personal target milestone.
   - Transparently labeled as a learner target, with explicit notice that official GPAT 2027 dates have not yet been gazetted by NBEMS.
   - Inline popover editor allows editing, validating dates in the past, and calculating remaining days with UTC midnight normalization.
4. **Interactive Recommended Study Choices:**
   - **Option A (Pharmacology — Forest Green):** "Autonomic nervous system" with dedicated `SynapseIllustration` displaying presynaptic bulbs, neurotransmitter quanta, and postsynaptic receptors. Tagged with *High yield*, *Concept practice*, and *GPAT relevant*.
   - **Option B (Pharmaceutics — Sky Blue):** "Dissolution & drug release" with dedicated `DissolutionIllustration` showing a graduated beaker, dissolving tablet, and Noyes-Whitney diffusion boundary layer particles. Tagged with *Core concept*, *Numerical practice*, and *Frequently asked*.
   - Both cards include 12-minute time estimates, rationale, instant session start button (`handleStartMission`), and direct syllabus explorer deep links.
5. **Unified "Your plan today" Panel (`UnifiedStudyPlanToday`):**
   - Matches the segmented reference controller:
     - **Studied Tab (Green Checkmark):** Displays verified learning activities logged today in SQLite (`learning_events` and `student_attempts`).
     - **Plan next Tab (Blue Plus):** Interactive study queue allowing students to queue upcoming topics with subject tags and estimated durations, stored in durable local storage (`gpat_learner_study_plan_v1`) without mutating official backend history.
6. **FSRS Review Buffer Card (`FsrsReviewSummaryCard`):**
   - Displays real-time due cards from `GET /api/study/review-queue` with violet/purple flashcard visual tokens and direct launch action into `/review`.
7. **Syllabus Subject Explorer Preview (`SyllabusSubjectExplorerPreview`):**
   - 5 colorful, thumb-friendly domain pills matching the approved palette:
     - **Pharmacology** (Green • Receptors • Drugs • Systems)
     - **Pharmaceutics** (Blue • Formulations • Delivery • QA)
     - **Pharmaceutical Chemistry** (Amber • Structures • Reactions • SAR)
     - **Pharmacognosy** (Violet • Natural products • Crude drugs)
     - **Biotechnology & Allied** (Teal • Molecular biology • Genetics)
   - Deep-links directly into `/study` with query filter parameters.

---

## 2. Quality & Verification Gates

| Gate | Target Requirement | Audit Outcome | Status |
|---|---|---|---|
| **ESLint Analysis** | 0 errors, 0 warnings (`npm run lint`) | 0 errors, 0 warnings | **PASS** |
| **Strict TypeScript** | Clean type-check (`npx tsc --noEmit`) | 0 type errors | **PASS** |
| **Next.js Production Build** | Compile all pages (`npm run build`) | All 11 pages compiled successfully in 2.4s | **PASS** |
| **HTTP Live Service** | Dev server responsiveness (`/today`) | Returned HTTP 200 with complete markup | **PASS** |
| **Backend Test Suite** | Pytest regression suite (`pytest tests/`) | 14/14 tests passed in 37.59s | **PASS** |
| **Database Integrity** | `PRAGMA integrity_check` on both DBs | Both `ok`, zero structural corruption | **PASS** |
| **Content Baseline Lock** | 2,063 questions | Exactly 2,063 verified | **PASS** |
| **Learner Baseline Safety** | Exact table row counts | Restored (`attempts=7, cards=11, events=10, sessions=3, goals=1, achievements=4`) | **PASS** |

---

## 3. Files Created & Updated

- [`web/src/components/today/botanical-illustrations.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/today/botanical-illustrations.tsx) — Vector artwork (`BotanicalHeroGraphic`, `SynapseIllustration`, `DissolutionIllustration`).
- [`web/src/components/today/exam-countdown-card.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/today/exam-countdown-card.tsx) — 2 Feb 2027 countdown with watermark and inline editor.
- [`web/src/components/today/fsrs-review-summary-card.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/today/fsrs-review-summary-card.tsx) — Violet flashcard review widget.
- [`web/src/components/today/two-study-choices-section.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/today/two-study-choices-section.tsx) — Green/Blue illustration study choice cards with micro-tags.
- [`web/src/components/today/unified-study-plan-today.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/today/unified-study-plan-today.tsx) — Segmented Studied vs Plan Next controller.
- [`web/src/components/today/syllabus-explorer-preview.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/today/syllabus-explorer-preview.tsx) — 5-domain color pills.
- [`web/src/components/layout/app-shell.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/components/layout/app-shell.tsx) — Enhanced sidebar with organic aspirant reminder card.
- [`web/src/app/today/page.tsx`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/app/today/page.tsx) — Unified living home screen orchestrator.
- [`web/src/lib/preferences.ts`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/lib/preferences.ts) — Defaulted targetExamDate to `2027-02-02`.
- [`web/src/app/globals.css`](file:///c:/Users/Home/Downloads/PROJECTS/SRE_APP/web/src/app/globals.css) — Dark navy surfaces and organic keyframe animations.
