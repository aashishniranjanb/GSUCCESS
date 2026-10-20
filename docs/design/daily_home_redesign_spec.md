# GPAT Learning OS — Phase 5A.1: Daily Home Redesign Specification

**Status:** Complete  
**Date:** 2026-10-19  
**Governing Standard:** `BEST_GPAT_UX.md`  
**Route:** `/today`

---

## 1. Executive Summary & Design Principles

The redesigned Start Page (`/today`) transforms the initial learner landing experience from a dense, card-heavy dashboard into an action-first, calming learning environment. It adheres strictly to the **5-Second Learner Clarity Test**:
1. **Where am I in my preparation?** — Answered immediately by the unified contextual countdown and retention status banner.
2. **What is the best next action?** — Communicated via a primary, non-distracting Mission Action Hero.
3. **Why is that action recommended?** — Explained with transparent rationale (balanced syllabus coverage, due FSRS reviews, and weak spots).
4. **How can I start immediately?** — Single, prominent primary CTA (`Start Daily Mission` or `Resume Mission`).

---

## 2. Visual Architecture & Design Language

- **Editorial & Botanical Foundation:** Deep botanical navy foundation (`#070d18` / `var(--color-bg-base)`) complemented by warm-editorial light theme support (`data-theme="light"` / `bg-[#fbfbf9]`).
- **Elimination of Visual Noise:**
  - Removed decorative AI gradients, glowing borders, and heavy backdrop blurs.
  - Replaced oversized (220px) top illustration banners with a purposeful greeting and inline iconography.
  - Eliminated redundant search inputs and extraneous profile/notification badges that distracted from primary study workflows.
- **Subject Color System:**
  - **Pharmacology:** Mint / Emerald (`#10b981`)
  - **Pharmaceutics:** Ocean Blue (`#3b82f6`)
  - **Pharmaceutical Chemistry:** Warm Amber (`#f59e0b`)
  - **Pharmacognosy:** Botanical Violet (`#8b5cf6`)
  - **Biotechnology:** Teal (`#14b8a6`)

---

## 3. Core Component Layout & Interactions

### 3.1 Learner Greeting & Primary Action Hero (`today/page.tsx`)
- Displays personalized greeting based on time of day and student profile.
- Dynamic CTA:
  - When in progress: **"Resume Mission (Question X/Y)"** with instant resume action.
  - When ready: **"Start Daily Mission (12 mins • 5 Qs)"**.
  - When completed: **"Retake Daily Mission"** or clear prompt to explore syllabus.
- Reassurance microcopy: *"Takes ~12 mins • Balances new syllabus coverage and due memory reviews."*

### 3.2 Contextual Study Status Row
- **Exam Countdown Card (`exam-countdown-card.tsx`):**
  - Configurable target date (defaulting to 2 February 2027).
  - Explicit **"Learner Target"** badge clarifying that official 2027 examination dates have not yet been gazetted by NBEMS.
  - Clean modal editor for updating the target exam date.
- **FSRS Memory Retention Card (`fsrs-review-summary-card.tsx`):**
  - Displays genuine flashcard review state (`X Due` vs `Up to date`).
  - One-click trigger to initiate spaced repetition review.

### 3.3 Personalized Focus Options (`two-study-choices-section.tsx`)
- **Option A (Daily Mission):** Direct, balanced study sprint with question provenance badges.
- **Option B (Targeted Spaced Review):** Prioritizes cards and concepts entering forgetting curves.
- No artificial gradients; leverages understated surface tokens (`var(--color-surface-base)`).

### 3.4 Today's Plan & Activity Log (`unified-study-plan-today.tsx`)
- **Studied Today:** Verified learning events recorded in session storage and backend telemetry.
- **Plan Next:** Local study queue saved on device for structured offline/online progression.
- Clear, plain-language labels replacing internal system jargon (e.g., replaced "SQLite Backed" with *"Verified learning events logged today"*).

### 3.5 Syllabus Exploration Bento (`syllabus-explorer-preview.tsx`)
- Presents genuine topic counts across the five core GPAT disciplines:
  - Pharmacology (39 topics)
  - Pharmaceutics (65 topics)
  - Pharmaceutical Chemistry (58 topics)
  - Pharmacognosy (27 topics)
  - Biotechnology (32 topics)
- Direct routing to `/learn` with subject-filter preselection.

---

## 4. Theme Inversion & Accessibility

- Fully verified color inversion supporting both Dark Botanical Navy and Editorial Warm White.
- High typographic contrast (WCAG AAA compliant text tokens).
- Responsive across all viewports (Mobile 360px–393px, Tablet 768px, Desktop 1366px+).
