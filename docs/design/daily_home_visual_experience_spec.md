# GPAT Learning OS — Home Page Visual Experience Specification

**Date:** 2026-10-19  
**Status:** Implemented & Verified  
**Governing Standard:** `BEST_GPAT_UX.md`  
**Target Route:** `/today`

---

## 1. Design Overview & Objectives

The Visual Experience Upgrade transforms `/today` into a distinctive, premium botanical study environment with clean typography, clear visual hierarchy, time-aware personalized greetings, and dedicated learner agency.

### Core Visual Principles
1. **Editorial Deep Navy Foundation:** Deep navy canvas (`#080B12`) accented with forest emerald (`#10b981`), ocean blue (`#3b82f6`), warm amber (`#f59e0b`), and violet (`#8b5cf6`). Full support for light and warm-editorial color inversion.
2. **Action-First Simplicity:** Single, prominent daily mission CTA visible on standard desktop and mobile viewports without cognitive clutter.
3. **Respectful Animation:** CSS-only staggered organic swaying and soft breathing pulses restricted to botanical illustrations. Fully disables when `prefers-reduced-motion: reduce` is detected.
4. **Transparent Learner Control:** Distinct separation between system-predicted focus recommendations and learner-planned study queues.

---

## 2. Key Component Architectural Specifications

### 2.1 Time-Aware Personalized Greeting & Hero (`daily-hero-section.tsx`)
- **Local Time Calculation:**
  - `05:00 - 11:59`: "Good morning!"
  - `12:00 - 16:59`: "Good afternoon!"
  - `17:00 - 21:59`: "Good evening!"
  - `22:00 - 04:59`: "Welcome back."
- **Hydration Safe:** Evaluated client-side after initial mount (`hasMounted` state) to prevent SSR hydration mismatches. Recalculates dynamically when window regains focus.
- **Personalized First Name:** Resolved from local user preferences (`localPrefs.learnerName`). Falls back to `Today, let's make progress.` if no name is configured.
- **Headline Emerald Highlight:** Highlights the key action verb `progress` with an understated emerald underline (`underline decoration-emerald-500/30`).
- **Responsive Layout:**
  - Desktop (1366px+): Two-column composition with headline, microcopy, and primary CTA on the left; stylized study scholar and botanical illustration on the right.
  - Mobile (360–393px): Stacked vertical layout keeping the primary action near the top without visual overlap.

### 2.2 Botanical Illustration & Subtle Animation (`botanical-illustrations.tsx`)
- High-fidelity inline SVG featuring a pharmacy scholar silhouette studying at a bench with subject-color codices (Green Pharmacology, Blue Pharmaceutics, Amber Chemistry), organic leaf stems, and glowing knowledge spores.
- Pure CSS keyframe animations: `.animate-sway` (gentle rotational sway) and `.animate-pulse-soft` (subtle scale/opacity breath).
- Accessibility: Hidden from assistive technology via `aria-hidden="true"`, with non-empty parent layout fallbacks.

### 2.3 Essential Review Card (`fsrs-review-summary-card.tsx`)
- **Renamed Title:** “Essential Review” (replaces internal "Due for review (FSRS)").
- **Supporting Text:** *“Revisit what you've learned to strengthen recall.”*
- **Authority:** Powered directly by authoritative backend `/api/review/queue` endpoint, displaying genuine active cards due today.

### 2.4 Dedicated "My Study Plan" Section (`my-study-plan-section.tsx`)
- **Learner Autonomy:** Allows learners to search the real GPAT syllabus taxonomy or enter custom topics, set session durations (10m, 15m, 20m, 30m), reorder items (up/down), toggle completion, or remove items.
- **Empty State:** *“Your plan starts here. Add a topic you want to study next.”*
- **Integrity Notice:** Explicitly clarifies that queuing topics is saved locally on device and does not fabricate mastery or official database attempts until sessions are completed.
- **Persistence:** Bound to durable `gpat_learner_study_plan_v1` local storage key.

### 2.5 Studied Today Activity Log (`studied-today-section.tsx`)
- Displays real, verified learning events recorded in session storage and backend telemetry today.
- Visual badges for correct recall vs review required.

---

## 3. Ordered Content Hierarchy

As defined in Section 7 of the governing specification:
1. Compact application header (AppShell).
2. Personalized greeting and botanical hero (`DailyHeroSection`).
3. Daily mission action (integrated into `DailyHeroSection`).
4. Compact study status: Configurable learner target date countdown (`ExamCountdownCard`).
5. Two recommended study choices: Option A & Option B (`TwoStudyChoicesSection`).
6. Essential Review (`FsrsReviewSummaryCard`).
7. My Study Plan (`MyStudyPlanSection`).
8. Studied today / recent activity (`StudiedTodaySection`).
9. Explore by subject (`SyllabusSubjectExplorerPreview`).
