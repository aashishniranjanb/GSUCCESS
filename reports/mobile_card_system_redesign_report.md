# GPAT 2027 — Mobile Card System Redesign Report

**Date:** 2026-10-19  
**Status:** Verification Passed (11/11 pytest passed, 0 lint errors, 0 lint warnings, 0 type errors, 3/3 SQLite PRAGMA integrity passed)  
**Governing Documents:** `BEST_GPAT_UX.md`, Phase 5A–5E Specifications  

---

## 1. Executive Summary

The mobile card system on `/today` (`web/src/app/today/page.tsx` and `web/src/components/today/`) has been redesigned according to three canonical card interaction patterns:
- **Pattern A (Featured Action Card):** Applied to the Daily Hero Section (`daily-hero-section.tsx`). Highlights the learner greeting, clear mission duration (`~12 mins`), practice question count, and a dominant primary CTA (`Start Daily Mission` / `Retake Daily Mission`) with zero clutter.
- **Pattern B (Compact Information Card):** Applied to `ExamCountdownCard` (Exam Horizon) and `FsrsReviewSummaryCard` (Essential Review). Features tight, readable hierarchy, high-contrast monospace counter metrics (`106 DAYS REMAINING`, `8 CARDS DUE TODAY`), and direct single-action affordances without nested card borders.
- **Pattern C (Discovery Card):** Applied to `TwoStudyChoicesSection` (Personalized Focus) and `SyllabusSubjectExplorerPreview` (Explore by Subject). Features clear subject badges, subtle botanical/scientific watermark illustrations, dominant "Start Mission" action, and quiet secondary "Details" actions. On mobile, `Explore by Subject` offers a smooth horizontal snap carousel with peek affordance (`w-[240px]` cards) indicating undiscovered items.

In addition, the **Studied Today** section has been redesigned to display a concise summary with a ceiling of **max 3 recent event rows** plus a direct "View all activity &rarr;" link pointing to `/progress`. No persisted historical records were truncated or deleted.

---

## 2. Card Patterns & Architecture

| Pattern | Component | Role & Treatment |
|---|---|---|
| **Pattern A: Featured Action** | `DailyHeroSection` | Deep navy & emerald glow, time-aware personalized greeting ("Good evening"), headline with accent underline, compact 144px pharmacy lab illustration crop, prominent primary CTA. |
| **Pattern B: Compact Information** | `ExamCountdownCard` | Exam Horizon showing countdown to configurable target date (`2027-02-02`), unconfirmed disclaimer notice, gear modal button. |
| **Pattern B: Compact Information** | `FsrsReviewSummaryCard` | Essential Review displaying real FSRS decay count (`8 Due`), interval explanation, and direct CTA (`Start Review Session`). |
| **Pattern C: Discovery Card** | `TwoStudyChoicesSection` | Personalized Focus options A & B with subject styling, duration chips, evidence badges, primary "Start Mission" button, and ghost "Details" button. |
| **Pattern C: Discovery Card** | `SyllabusSubjectExplorerPreview` | Horizontal snap rail on mobile (`snap-x snap-mandatory`), desktop responsive grid; displays topic counts and "Browse &rarr;" affordance. |
| **Compact History** | `StudiedTodaySection` | Limits feed to latest 3 events on the home page, displays aggregate count & accuracy, and links to `/progress` for full historical drill-down. |

---

## 3. Viewport Verification

All layouts and card states were visually verified across 4 target viewports using headless Chromium via Playwright:

1. **Mobile Narrow (360x800):**
   - First Viewport: `reports/screenshots/mobile_card_system/360x800_viewport.png`
   - Full Page: `reports/screenshots/mobile_card_system/360x800_full.png`
   - Verification: Greeting, headline, primary CTA, and illustration fit neatly within first viewport; bottom navigation has 5 items with safe area padding (`pb-24`) without obscuring the exam card.
2. **Mobile Standard (393x852 - iPhone 14/15/16):**
   - First Viewport: `reports/screenshots/mobile_card_system/393x852_viewport.png`
   - Full Page: `reports/screenshots/mobile_card_system/393x852_full.png`
   - Verification: Clear typographic hierarchy, touch targets `>= 48px`, horizontal cards peek smoothly.
3. **Tablet (768x1024 - iPad Mini / Air):**
   - First Viewport: `reports/screenshots/mobile_card_system/768x1024_viewport.png`
   - Full Page: `reports/screenshots/mobile_card_system/768x1024_full.png`
   - Verification: Left sidebar desktop navigation active, 2-column grid for Compact Cards and Personalized Focus cards.
4. **Desktop (1366x900 - Laptop / Standard Monitor):**
   - First Viewport: `reports/screenshots/mobile_card_system/1366x900_viewport.png`
   - Full Page: `reports/screenshots/mobile_card_system/1366x900_full.png`
   - Verification: Max container constrained to `max-w-5xl`, side-by-side hero layout, 5-column syllabus subject explorer grid.

---

## 4. Quality & Regression Gate Results

- **ESLint & TypeScript:**
  - `npm run lint`: 0 errors, 0 warnings.
  - `npx tsc --noEmit`: 0 type errors.
- **Backend Regression Suite:**
  - `pytest tests/verification/test_phase5e_progress_readiness.py tests/verification/test_phase5d_mini_mock.py -v`:
    - 11 passed in 15.31s.
- **Database Integrity:**
  - `gpat_knowledge.db`: `('ok',)`
  - `data/gpat_baseline.db`: `('ok',)`
  - `data/pyq_topic_staging.db`: `('ok',)`
